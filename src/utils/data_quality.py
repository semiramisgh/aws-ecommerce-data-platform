import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "ecommerce"

ENTITY_RULES = {
    "products": {
        "payload_key": "products",
        "required_fields": {"id", "title", "price"},
    },
    "customers": {
        "payload_key": "users",
        "required_fields": {"id", "firstName", "lastName", "email"},
    },
    "orders": {
        "payload_key": "carts",
        "required_fields": {"id", "userId", "products", "total"},
    },
}


class DataQualityError(ValueError):
    pass


def validate_document(document: dict[str, Any], entity: str) -> int:
    if entity not in ENTITY_RULES:
        raise DataQualityError(f"Unknown entity: {entity}")

    metadata = document.get("metadata")
    payload = document.get("payload")

    if not isinstance(metadata, dict):
        raise DataQualityError("Missing or invalid metadata")

    if not isinstance(payload, dict):
        raise DataQualityError("Missing or invalid payload")

    if metadata.get("entity") != entity:
        raise DataQualityError(
            f"Metadata entity does not match directory: {entity}"
        )

    rules = ENTITY_RULES[entity]
    records = payload.get(rules["payload_key"])

    if not isinstance(records, list) or not records:
        raise DataQualityError(f"No {entity} records found")

    expected_count = metadata.get("record_count")

    if expected_count != len(records):
        raise DataQualityError(
            f"Record count mismatch: metadata={expected_count}, "
            f"actual={len(records)}"
        )

    required_fields = rules["required_fields"]

    for index, record in enumerate(records):
        missing_fields = required_fields - record.keys()

        if missing_fields:
            raise DataQualityError(
                f"{entity} record {index} is missing fields: "
                f"{sorted(missing_fields)}"
            )

    record_ids = [record["id"] for record in records]

    if len(record_ids) != len(set(record_ids)):
        raise DataQualityError(f"Duplicate IDs found in {entity}")

    return len(records)


def main() -> None:
    total_files = 0

    for entity in ENTITY_RULES:
        entity_directory = RAW_ROOT / entity
        files = sorted(entity_directory.glob("*.json"))

        if not files:
            raise DataQualityError(
                f"No local JSON files found for {entity}"
            )

        for file_path in files:
            with file_path.open("r", encoding="utf-8") as file:
                document = json.load(file)

            record_count = validate_document(document, entity)
            total_files += 1

            print(
                f"Passed: {file_path.name} "
                f"({record_count} {entity} records)"
            )
    print(f"All data quality checks passed for {total_files} files")

if __name__ == "__main__":
    main()