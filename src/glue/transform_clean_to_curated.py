from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_ROOT = PROJECT_ROOT / "data" / "clean"
CURATED_ROOT = PROJECT_ROOT / "data" / "curated"


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("ecommerce-clean-to-curated")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        orders = spark.read.parquet(
            str(CLEAN_ROOT / "orders")
        )
        customers = spark.read.parquet(
            str(CLEAN_ROOT / "customers")
        )
        products = spark.read.parquet(
            str(CLEAN_ROOT / "products")
        )

        order_lines = orders.select(
            F.col("order_id").cast("long"),
            F.col("userId").cast("long").alias("customer_id"),
            F.col("total").cast("double").alias("order_gross_amount"),
            F.col("discountedTotal").cast("double").alias(
                "order_net_amount"
            ),
            F.col("ingested_at"),
            F.col("ingestion_date"),
            F.explode_outer("products").alias("line_item"),
        ).withColumn(
            "product_id",
            F.col("line_item.id").cast("long"),
        )

        customer_dimension = customers.select(
            F.col("customer_id").cast("long"),
            F.concat_ws(
                " ",
                F.col("firstName"),
                F.col("lastName"),
            ).alias("customer_name"),
            F.col("email").alias("customer_email"),
        )

        product_dimension = products.select(
            F.col("product_id").cast("long"),
            F.col("title").alias("catalog_product_title"),
            F.col("category"),
        )

        sales = (
            order_lines
            .join(
                customer_dimension,
                on="customer_id",
                how="left",
            )
            .join(
                product_dimension,
                on="product_id",
                how="left",
            )
            .select(
                "order_id",
                "customer_id",
                "customer_name",
                "customer_email",
                "product_id",
                F.coalesce(
                    F.col("catalog_product_title"),
                    F.col("line_item.title"),
                ).alias("product_title"),
                "category",
                F.col("line_item.quantity")
                .cast("int")
                .alias("quantity"),
                F.col("line_item.price")
                .cast("double")
                .alias("unit_price"),
                F.col("line_item.total")
                .cast("double")
                .alias("gross_amount"),
                F.col("line_item.discountPercentage")
                .cast("double")
                .alias("discount_percentage"),
                F.col("line_item.discountedTotal")
                .cast("double")
                .alias("net_amount"),
                "order_gross_amount",
                "order_net_amount",
                "ingested_at",
                "ingestion_date",
            )
            .dropDuplicates(["order_id", "product_id"])
        )

        output_path = CURATED_ROOT / "sales"

        (
            sales.write
            .mode("overwrite")
            .partitionBy("ingestion_date")
            .parquet(str(output_path))
        )

        print(f"Curated sales records: {sales.count()}")
        print(f"Output: {output_path}")
        print("Clean-to-curated transformation completed successfully")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()