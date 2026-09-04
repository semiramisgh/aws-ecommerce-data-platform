from collections.abc import Callable

from src.ingestion.extract_api import main as extract_data
from src.ingestion.upload_to_s3 import main as upload_data
from src.utils.data_quality import main as validate_data


def run_stage(stage_name: str, stage_function: Callable[[], None]) -> None:
    print(f"\n{'=' * 60}")
    print(f"Starting stage: {stage_name}")
    print("=" * 60)

    stage_function()

    print(f"Completed stage: {stage_name}")


def main() -> None:
    print("Starting AWS e-commerce ingestion pipeline")

    run_stage("Extract data from API", extract_data)
    run_stage("Validate data quality", validate_data)
    run_stage("Upload raw data to S3", upload_data)

    print("\nPipeline completed successfully")


if __name__ == "__main__":
    main()