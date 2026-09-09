import json
import logging
import os
from urllib.parse import unquote_plus

import boto3

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

    workflow_run_id = None

    if processed_objects:
       workflow_name = os.environ["GLUE_WORKFLOW_NAME"]
       glue_client = boto3.client("glue")
       workflow_response = glue_client.start_workflow_run(Name=workflow_name)
       workflow_run_id = workflow_response["RunId"]

       logger.info(
         "Glue workflow started: name=%s run_id=%s",
         workflow_name,
         workflow_run_id,
       )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "S3 event processed successfully",
                "processed_count": len(processed_objects),
                "workflow_run_id": workflow_run_id,
                "objects": processed_objects,
            }
        ),
    }
