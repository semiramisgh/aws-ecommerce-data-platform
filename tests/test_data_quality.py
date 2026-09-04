import pytest

from src.utils.data_quality import DataQualityError, validate_document


def make_document(entity, payload_key, records):
    return {
        "metadata": {
            "entity": entity,
            "record_count": len(records),
        },
        "payload": {
            payload_key: records,
        },
    }


def test_valid_products_document():
    document = make_document(
        "products",
        "products",
        [
            {"id": 1, "title": "Laptop", "price": 999.0},
            {"id": 2, "title": "Phone", "price": 499.0},
        ],
    )

    assert validate_document(document, "products") == 2


def test_record_count_mismatch():
    document = make_document(
        "products",
        "products",
        [{"id": 1, "title": "Laptop", "price": 999.0}],
    )
    document["metadata"]["record_count"] = 2

    with pytest.raises(DataQualityError, match="Record count mismatch"):
        validate_document(document, "products")


def test_missing_required_field():
    document = make_document(
        "customers",
        "users",
        [
            {
                "id": 1,
                "firstName": "Sara",
                "lastName": "Test",
            }
        ],
    )

    with pytest.raises(DataQualityError, match="missing fields"):
        validate_document(document, "customers")


def test_duplicate_ids():
    document = make_document(
        "orders",
        "carts",
        [
            {
                "id": 1,
                "userId": 10,
                "products": [],
                "total": 0,
            },
            {
                "id": 1,
                "userId": 11,
                "products": [],
                "total": 0,
            },
        ],
    )

    with pytest.raises(DataQualityError, match="Duplicate IDs"):
        validate_document(document, "orders")