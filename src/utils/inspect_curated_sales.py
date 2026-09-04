from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_PATH = PROJECT_ROOT / "data" / "curated" / "sales"


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("inspect-curated-sales")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        sales = spark.read.parquet(str(SALES_PATH))

        record_count = sales.count()
        total_revenue = sales.agg(
            F.round(F.sum("net_amount"), 2).alias("total_revenue")
        ).first()["total_revenue"]

        duplicate_count = (
            sales.groupBy("order_id", "product_id")
            .count()
            .filter(F.col("count") > 1)
            .count()
        )

        print(f"Curated sales records: {record_count}")
        print(f"Total line-item revenue: {total_revenue}")
        print(f"Duplicate order/product pairs: {duplicate_count}")

        sales.groupBy("category").agg(
            F.round(F.sum("net_amount"), 2).alias("revenue"),
            F.sum("quantity").alias("units_sold"),
        ).orderBy(
            F.desc("revenue")
        ).show(
            10,
            truncate=False,
        )

        if record_count == 0:
            raise ValueError("Curated sales dataset is empty")

        if duplicate_count != 0:
            raise ValueError("Duplicate order/product pairs found")

        print("Curated sales validation passed")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()