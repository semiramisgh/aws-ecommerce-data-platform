import json
from importlib import import_module


lambda_module = import_module("src.lambda.raw_ingestion_monitor")


def test_lambda_handler_processes_s3_event():
    event = {
        "Records": [
            {
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "test-bucket",
                    },
                    "object": {
                        "key": (
                            "raw/ecommerce/orders/"
                            "ingestion_date%3D2026-09-04/"
                            "orders.json"
                        ),
                        "size": 483,
                    },
                },
            }
        ]
    }

    response = lambda_module.lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["processed_count"] == 1
    assert body["objects"][0]["bucket"] == "test-bucket"
    assert body["objects"][0]["key"] == (
        "raw/ecommerce/orders/"
        "ingestion_date=2026-09-04/"
        "orders.json"
    )
    assert body["objects"][0]["size"] == 483