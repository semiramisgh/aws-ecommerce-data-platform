from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    explode,
    input_file_name,
    row_number,
    to_date,
    to_timestamp,
)
from pyspark.sql.window import Window


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "ecommerce"
CLEAN_ROOT = PROJECT_ROOT / "data" / "clean"

ENTITY_CONFIG = {
    "products": {
        "payload_key": "products",
        "id_column": "product_id",
    },
    "customers": {
        "payload_key": "users",
        "id_column": "customer_id",
    },
    "orders": {
        "payload_key": "carts",
        "id_column": "order_id",
    },
}


def transform_entity(
    spark: SparkSession,
    entity: str,
    payload_key: str,
    id_column: str,
 ) -> DataFrame:
    input_pattern = str(RAW_ROOT / entity / "*.json")

    documents = (
        spark.read
        .option("multiLine", "true")
        .json(input_pattern)
    )

    flattened = (
        documents
            .select(
                to_timestamp(
                    col("metadata.ingested_at")
                ).alias("ingested_at"),
                input_file_name().alias("source_file"),
                explode(
                    col(f"payload.{payload_key}")
                ).alias("record"),
            )
            .select(
                "record.*",
                "ingested_at",
                "source_file",
            )
            .withColumnRenamed("id", id_column)
            .withColumn(
                "ingestion_date",
                to_date(col("ingested_at")),
            )
    )

    latest_record_window = (
        Window
        .partitionBy(id_column)
        .orderBy(
            col("ingested_at").desc(),
            col("source_file").desc(),
        )
    )

    return (
        flattened
        .withColumn(
            "_row_number",
            row_number().over(latest_record_window),
        )
        .filter(col("_row_number") == 1)
        .drop("_row_number")
    )


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("aws-ecommerce-raw-to-clean")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        for entity, config in ENTITY_CONFIG.items():
            clean_dataframe = transform_entity(
                spark=spark,
                entity=entity,
                payload_key=config["payload_key"],
                id_column=config["id_column"],
            )

            clean_dataframe.cache()
            record_count = clean_dataframe.count()

            output_directory = CLEAN_ROOT / entity

            (
                clean_dataframe.write
                .mode("overwrite")
                .partitionBy("ingestion_date")
                .parquet(str(output_directory))
            )

            clean_dataframe.unpersist()

            print(
                f"Cleaned {entity}: {record_count} records "
                f"written to {output_directory}"
            )

        print("Raw-to-clean transformation completed successfully")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()