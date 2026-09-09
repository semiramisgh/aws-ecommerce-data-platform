import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


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

    orders = spark.read.parquet(
        f"s3://{bucket_name}/clean/orders/"
    )
    customers = spark.read.parquet(
        f"s3://{bucket_name}/clean/customers/"
    )
    products = spark.read.parquet(
        f"s3://{bucket_name}/clean/products/"
    )

    order_lines = orders.select(
        F.col("order_id").cast("long"),
        F.col("userId").cast("long").alias("customer_id"),
        F.col("total").cast("double").alias(
            "order_gross_amount"
        ),
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

    output_path = f"s3://{bucket_name}/curated/sales/"

    (
        sales.write
        .mode("overwrite")
        .partitionBy("ingestion_date")
        .parquet(output_path)
    )

    logger.info(
        f"Curated sales data written successfully to {output_path}"
    )

    job.commit()


if __name__ == "__main__":
    main()