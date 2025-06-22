import boto3
import os
import json
import uuid
import time

# AWS clients
sqs = boto3.client('sqs')

# Environment variables
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def handler(event, context):
    """
    This function is triggered by a POST request to /ingest.
    It accepts a JSON body with comments and pushes them to SQS.
    """
    try:
        body = json.loads(event.get('body', '{}'))
        comments_to_ingest = body.get('comments', [])

        # Allow ingesting a single comment string as well
        if isinstance(comments_to_ingest, str):
            comments_to_ingest = [comments_to_ingest]

        if not isinstance(comments_to_ingest, list) or not comments_to_ingest:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body must contain a non-empty "comments" field as a string or a list of strings.'})
            }
        
        original_count = len(comments_to_ingest)
        print(f"Received {original_count} comments to ingest.")

        entries = []
        skipped_count = 0
        for comment_text in comments_to_ingest:
            if not isinstance(comment_text, str):
                print(f"Skipping non-string item in comments list: {comment_text}")
                skipped_count += 1
                continue
            
            # This is the standard comment structure our fetcher creates
            message_payload = {
                "comment_id": f"manual-{uuid.uuid4()}",
                "user_name": "manual_tester",
                "text": comment_text,
                "timestamp": int(time.time()),
            }
            entries.append({
                'Id': str(uuid.uuid4()),
                'MessageBody': json.dumps(message_payload)
            })

        processed_count = len(entries)
        print(f"Processing summary: {original_count} received, {skipped_count} skipped, {processed_count} processed")

        if not entries:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid comments to process after filtering.'})
            }

        sqs.send_message_batch(QueueUrl=SQS_QUEUE_URL, Entries=entries)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Successfully ingested {processed_count} comments.",
                'details': {
                    'original_count': original_count,
                    'skipped_count': skipped_count,
                    'processed_count': processed_count
                }
            })
        }

    except json.JSONDecodeError:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON in request body.'})}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': 'An internal server error occurred.'})}
