import boto3
import os
import json
import time
import random
import uuid
from datetime import datetime, timezone

# AWS clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
COMMENTS_TABLE_NAME = os.environ['COMMENTS_TABLE_NAME']
LIVE_PLATFORM_API_ENDPOINT = os.environ['LIVE_PLATFORM_API_ENDPOINT']

STATE_KEY = "comment_fetcher_state"

def handler(event, context):
    """
    This function is triggered by EventBridge.
    It fetches new comments from a live platform API and pushes them to an SQS queue.
    """
    table = dynamodb.Table(COMMENTS_TABLE_NAME)

    # 1. Get the last fetched timestamp from DynamoDB
    try:
        response = table.get_item(Key={'comment_id': STATE_KEY})
        last_fetched_timestamp = int(response.get('Item', {}).get('last_fetched_timestamp', 0))
    except Exception as e:
        print(f"Could not retrieve state. Defaulting to 0. Error: {e}")
        last_fetched_timestamp = 0

    print(f"Fetching comments since timestamp: {last_fetched_timestamp}")

    # 2. Mock calling the live platform API
    # In a real scenario, you would make an HTTP request like:
    # response = requests.get(LIVE_PLATFORM_API_ENDPOINT, params={'since': last_fetched_timestamp})
    # new_comments = response.json()
    new_comments = _get_mock_comments(last_fetched_timestamp)
    
    if not new_comments:
        print("No new comments found.")
        return {'statusCode': 200, 'body': 'No new comments.'}

    # 3. Push new comments to SQS
    entries = []
    for comment in new_comments:
        entries.append({
            'Id': str(uuid.uuid4()),
            'MessageBody': json.dumps(comment)
        })

    try:
        sqs.send_message_batch(QueueUrl=SQS_QUEUE_URL, Entries=entries)
        print(f"Successfully sent {len(entries)} comments to SQS.")
    except Exception as e:
        print(f"Error sending messages to SQS: {e}")
        # Depending on requirements, you might want to retry or handle this error differently
        return {'statusCode': 500, 'body': 'Failed to send messages to SQS.'}

    # 4. Update the last fetched timestamp in DynamoDB
    new_latest_timestamp = max(c['timestamp'] for c in new_comments)
    try:
        table.put_item(
            Item={
                'comment_id': STATE_KEY,
                'last_fetched_timestamp': new_latest_timestamp
            }
        )
        print(f"Successfully updated last fetched timestamp to: {new_latest_timestamp}")
    except Exception as e:
        print(f"Error updating state in DynamoDB: {e}")
        # This is not ideal, as we might re-process comments next run.
        # A more robust solution might involve a transactional approach or more resilient state management.

    return {'statusCode': 200, 'body': f'Processed {len(new_comments)} comments.'}


def _get_mock_comments(since_timestamp):
    """Generates some mock comments for demonstration purposes."""
    mock_comments = []
    current_time = int(time.time())
    
    # Only generate comments if it's been a little while
    if current_time - since_timestamp < 5:
        return []

    for i in range(random.randint(1, 5)):
        user = random.choice(["Alex", "Ben", "Charlie", "Dana", "Echo"])
        comment_text = random.choice([
            "How much is this?",
            "Is there a warranty?",
            "What colors are available?",
            "This looks amazing!",
            "I have a question about shipping.",
            "This is a useless comment.",
            "Tell me more about the material.",
            "bad word",
        ])
        ts = current_time + i
        mock_comments.append({
            "comment_id": f"comment-{ts}-{uuid.uuid4()}",
            "user_name": user,
            "text": comment_text,
            "timestamp": ts,
        })
    return mock_comments
