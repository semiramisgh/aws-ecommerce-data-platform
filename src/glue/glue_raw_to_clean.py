import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
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
    bucket_name: str,
    entity: str,
    payload_key: str,
    id_column: str,
) -> tuple[DataFrame, int]:
    input_path = (
        f"s3://{bucket_name}/raw/ecommerce/{entity}/"
    )
    output_path = (
        f"s3://{bucket_name}/clean/{entity}/"
    )

    documents = (
        spark.read
        .option("multiLine", "true")
        .option("recursiveFileLookup", "true")
        .json(input_path)
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

    clean_data = (
        flattened
        .withColumn(
            "_row_number",
            row_number().over(latest_record_window),
        )
        .filter(col("_row_number") == 1)
        .drop("_row_number")
    )

    clean_data.cache()
    record_count = clean_data.count()

    (
        clean_data.write
        .mode("overwrite")
        .partitionBy("ingestion_date")
        .parquet(output_path)
    )

    clean_data.unpersist()

    return clean_data, record_count


def main() -> None:
    args = getResolvedOptions(
        sys.argv,
        [
            "JOB_NAME",
            "S3_BUCKET_NAME",
        ],
    )

    spark_context = SparkContext.getOrCreate()
    glue_context = GlueContext(spark_context)
    spark = glue_context.spark_session
    logger = glue_context.get_logger()

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    bucket_name = args["S3_BUCKET_NAME"]

    for entity, config in ENTITY_CONFIG.items():
        _, record_count = transform_entity(
            spark=spark,
            bucket_name=bucket_name,
            entity=entity,
            payload_key=config["payload_key"],
            id_column=config["id_column"],
        )

        logger.info(f"Cleaned {record_count} records for entity {entity}")

    job.commit()


if __name__ == "__main__":
    main()