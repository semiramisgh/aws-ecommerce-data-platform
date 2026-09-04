import json
import logging
from urllib.parse import unquote_plus


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    processed_objects = []

    for record in event.get("Records", []):
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = unquote_plus(record["s3"]["object"]["key"])
        object_size = record["s3"]["object"].get("size", 0)
        event_name = record.get("eventName", "unknown")

        logger.info(
            "Raw object received: bucket=%s key=%s size=%s event=%s",
            bucket_name,
            object_key,
            object_size,
            event_name,
        )

        processed_objects.append(
            {
                "bucket": bucket_name,
                "key": object_key,
                "size": object_size,
                "event": event_name,
            }
        )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "S3 event processed successfully",
                "processed_count": len(processed_objects),
                "objects": processed_objects,
            }
        ),
    }