import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "data" / "raw" / "ecommerce"

RESOURCES = {
    "products": {
        "url": (
            "https://dummyjson.com/products"
            "?limit=0&select=id,title,description,category,price,"
            "discountPercentage,rating,stock,brand,sku"
        ),
        "data_key": "products",
        "source_resource": "products",
    },
    "customers": {
        "url": (
            "https://dummyjson.com/users"
            "?limit=0&select=id,firstName,lastName,age,gender,email,company"
        ),
        "data_key": "users",
        "source_resource": "users",
    },
    "orders": {
        "url": "https://dummyjson.com/carts?limit=0",
        "data_key": "carts",
        "source_resource": "carts",
    },
}


def create_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def main() -> None:
    session = create_session()
    ingestion_time = datetime.now(timezone.utc)
    run_id = ingestion_time.strftime("%Y%m%dT%H%M%SZ")

    for entity, config in RESOURCES.items():
        response = session.get(config["url"], timeout=30)
        response.raise_for_status()
        payload = response.json()

        output_directory = OUTPUT_ROOT / entity
        output_directory.mkdir(parents=True, exist_ok=True)

        output_file = output_directory / f"{entity}_{run_id}.json"

        raw_document = {
            "metadata": {
                "entity": entity,
                "source": "dummyjson",
                "source_resource": config["source_resource"],
                "ingested_at": ingestion_time.isoformat(),
                "record_count": len(payload[config["data_key"]]),
            },
            "payload": payload,
        }

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(raw_document, file, indent=2, ensure_ascii=False)

        print(
            f"Extracted {raw_document['metadata']['record_count']} "
            f"{entity} records -> {output_file}"
        )


if __name__ == "__main__":
    main()