import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "ecommerce"


def object_exists(s3_client, bucket_name: str, object_key: str) -> bool:
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as error:
        status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status_code == 404:
            return False

        raise


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    bucket_name = os.getenv("S3_BUCKET_NAME")
    profile_name = os.getenv("AWS_PROFILE", "aws-data-platform")
    region_name = os.getenv("AWS_REGION", "eu-central-1")

    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME is missing from the .env file")

    session = boto3.Session(
        profile_name=profile_name,
        region_name=region_name,
    )
    s3_client = session.client("s3")

    uploaded_count = 0
    skipped_count = 0

    for entity in ("products", "customers", "orders"):
        entity_directory = LOCAL_RAW_ROOT / entity

        for file_path in sorted(entity_directory.glob("*.json")):
            with file_path.open("r", encoding="utf-8") as file:
                document = json.load(file)

            ingestion_date = document["metadata"]["ingested_at"][:10]

            object_key = (
                f"raw/ecommerce/{entity}/"
                f"ingestion_date={ingestion_date}/"
                f"{file_path.name}"
            )

            if object_exists(s3_client, bucket_name, object_key):
                print(f"Skipped existing file: s3://{bucket_name}/{object_key}")
                skipped_count += 1
                continue

            s3_client.upload_file(
                str(file_path),
                bucket_name,
                object_key,
                ExtraArgs={
                    "ContentType": "application/json",
                        "Metadata": {
                            "source": "dummyjson",
                            "entity": entity,
                        },
                    },
            )

            print(f"Uploaded: s3://{bucket_name}/{object_key}")
            uploaded_count += 1

    print(
        f"Finished: {uploaded_count} uploaded, "
        f"{skipped_count} skipped"
    )


if __name__ == "__main__":
 main()