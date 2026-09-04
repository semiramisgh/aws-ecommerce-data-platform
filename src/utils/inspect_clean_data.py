from pathlib import Path

from pyspark.sql import SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_ROOT = PROJECT_ROOT / "data" / "clean"

DISPLAY_COLUMNS = {
    "products": [
        "product_id",
        "title",
        "category",
        "price",
        "stock",
        "ingestion_date",
    ],
    "customers": [
        "customer_id",
        "firstName",
        "lastName",
        "email",
        "ingestion_date",
    ],
    "orders": [
        "order_id",
        "userId",
        "total",
        "totalProducts",
        "totalQuantity",
        "ingestion_date",
    ],
}


def main() -> None:
    spark = (
        SparkSession.builder
            .appName("inspect-clean-data")
            .master("local[*]")
            .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        for entity, columns in DISPLAY_COLUMNS.items():
            dataframe = spark.read.parquet(
                str(CLEAN_ROOT / entity)
        )

        print(f"\n{entity.upper()}")
        print(f"Record count: {dataframe.count()}")

        dataframe.select(*columns).show(
            3,
            truncate=False,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()