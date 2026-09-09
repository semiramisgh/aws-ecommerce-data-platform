# AWS E-Commerce Data Platform

[![Python tests](https://github.com/semiramishg/aws-ecommerce-data-platform/actions/workflows/tests.yml/badge.svg)](https://github.com/semiramishg/aws-ecommerce-data-platform/actions/workflows/tests.yml)
[![Terraform Checks](https://github.com/semiramishg/aws-ecommerce-data-platform/actions/workflows/terraform.yml/badge.svg)](https://github.com/semiramishg/aws-ecommerce-data-platform/actions/workflows/terraform.yml)

An end-to-end AWS data engineering project that ingests synthetic e-commerce data, processes it through raw, clean, and curated data layers, and makes it available for serverless analytics.

## Architecture

```mermaid
flowchart TD
A["REST API and CSV"] --> B["Python ingestion"]
B --> C["Amazon S3 Raw - JSON"]
C --> D["AWS Lambda"]
D --> E["Amazon CloudWatch"]
D --> F["AWS Glue Workflow"]
F --> G["On-demand Trigger"]
G --> H["Raw-to-Clean Glue Job"]
H --> I["Amazon S3 Clean - Parquet"]
I --> J["AWS Glue Data Catalog"]
J --> K["Amazon Athena"]
H --> L["Conditional Trigger on Success"]
L --> M["Clean-to-Curated Glue Job"]
M --> N["Amazon S3 Curated Sales"]
N --> O["AWS Glue Data Catalog"]
O --> P["Amazon Athena Analytics"]
```

## Data Layers

| Layer | Format | Purpose |
|---|---|---|
| Raw | JSON | Preserves the original ingested API and CSV data |
| Clean | Parquet | Stores validated and standardized customers, orders, and products |
| Curated | Partitioned Parquet | Provides an analytics-ready sales dataset enriched with customer and product information |

The curated sales dataset is partitioned by `ingestion_date` to reduce the amount of data scanned by analytical queries.

## Implemented Workflow
The pipeline is automated with AWS Glue Workflow and event-driven Lambda orchestration:

1. Ingest synthetic customer, order, and product data using Python.
2. Upload the source data to the Amazon S3 raw layer.
3. Process S3 events with AWS Lambda and record monitoring information in CloudWatch.
4. Start the AWS Glue Workflow automatically from Lambda.
5. Run the raw-to-clean Glue job through an on-demand workflow trigger.
6. Start the clean-to-curated Glue job only after the raw-to-clean job succeeds.
7. Transform raw JSON data into clean Parquet datasets using AWS Glue and PySpark.
8. Discover clean datasets with AWS Glue Crawlers and validate them using Amazon Athena.
9. Join orders, customers, and products into a curated sales dataset.
10. Write partitioned Parquet files to the S3 curated layer.
11. Register the curated dataset in the AWS Glue Data Catalog.
12. Run analytical SQL queries using Amazon Athena.

## Analytics Results

The completed pipeline produced:

- 788 curated sales line items
- 208 distinct orders
- 24 product categories
- Total net revenue of 3,447,183.80
- No duplicate order-product combinations in the validated curated dataset

Example business analyses include:

- Revenue and units sold by product category
- Top products by net revenue
- Top customers by revenue
- Validation of record counts and financial totals

## Technologies

- Python
- PySpark
- SQL
- Amazon S3
- AWS Lambda
- AWS Glue ETL
- AWS Glue Crawlers
- AWS Glue Data Catalog
- Amazon Athena
- Amazon CloudWatch
- AWS CLI
- Git and GitHub
- Terraform
- GitHub Actions

## Project Structure

```text
.
├── .github/
│ └── workflows/
│ ├── terraform.yml
│ └── tests.yml
├── architecture/
│ └── decisions/
├── bootstrap/
│ └── main.tf
├── data/
│ └── sample/
├── docs/
├── infrastructure/
│ ├── crawlers.tf
│ ├── glue.tf
│ ├── iam.tf
│ ├── jobs.tf
│ ├── lambda.tf
│ ├── lambda_iam.tf
│ ├── lambda_trigger.tf
│ ├── monitoring.tf
| |── orchestration.tf
│ ├── providers.tf
│ ├── s3.tf
│ ├── variables.tf
│ └── versions.tf
├── sql/
│ └── athena/
├── src/
│ ├── glue/
│ ├── ingestion/
│ ├── lambda/
│ ├── utils/
│ └── run_pipeline.py
├── tests/
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

## Infrastructure as Code

Terraform manages the AWS resources used by the data platform, including:

- Amazon S3 data-lake configuration
- AWS Glue databases, crawlers, jobs, IAM roles, and policies
- AWS Lambda function, IAM resources, and S3 event notification
- Amazon CloudWatch log-group configuration

A separate `bootstrap` Terraform configuration creates the remote-state S3 bucket. The backend uses:

- Amazon S3 server-side encryption
- S3 versioning
- S3 native state locking
- Public-access blocking
- `prevent_destroy` protection for critical resources

Existing AWS resources were imported into Terraform and reconciled until both Terraform configurations returned `No changes`.

GitHub Actions automatically runs `terraform fmt`, backend-free initialization, and `terraform validate` for both `bootstrap` and `infrastructure`.

## SQL Analytics

Athena queries are stored in `sql/athena/`:

- `01_validate_clean_counts.sql`
- `02_top_customers_by_revenue.sql`
- `03_validate_curated_sales.sql`
- `04_revenue_by_category.sql`
- `05_top_products_by_revenue.sql`

## Reliability and Cost Controls

The project uses:

- Parquet columnar storage
- Date-based partitioning
- Data-quality validation
- CloudWatch logging
- Minimal Glue worker capacity
- Short Glue job timeouts
- On-demand Glue Crawlers
- Athena queries that scan only small Parquet datasets
- Environment variables for configuration
- No credentials or secrets committed to Git

## Project Status

The core end-to-end data pipeline is complete:

- [x] Data ingestion
- [x] S3 raw layer
- [x] Lambda monitoring
- [x] Raw-to-clean Glue transformation
- [x] Clean Glue Data Catalog
- [x] Athena clean-data validation
- [x] Clean-to-curated Glue transformation
- [x] Curated Glue Data Catalog
- [x] Athena business analytics
- [x] Automated orchestration
- [x] Infrastructure as Code
- [x] Secure remote Terraform state
- [x] Terraform CI validation
- [ ] BI dashboard
- [x] Automated tests
