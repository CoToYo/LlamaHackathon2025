import boto3
import os
import json

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
COMMENTS_TABLE_NAME = os.environ['COMMENTS_TABLE_NAME']

def handler(event, context):
    """
    This function is triggered by a POST request to /responses/{comment_id}/ack.
    It marks a comment as 'CONSUMED' in DynamoDB.
    """
    table = dynamodb.Table(COMMENTS_TABLE_NAME)

    # 1. Get comment_id from the path parameters
    try:
        comment_id = event['pathParameters']['comment_id']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'comment_id not found in path'})
        }

    print(f"Acknowledging comment with ID: {comment_id}")

    # 2. Update the item's status to 'CONSUMED'
    try:
        response = table.update_item(
            Key={'comment_id': comment_id},
            UpdateExpression="set #s = :s",
            ExpressionAttributeNames={
                '#s': 'status'
            },
            ExpressionAttributeValues={
                ':s': 'CONSUMED'
            },
            # Condition to ensure the item exists before updating
            ConditionExpression="attribute_exists(comment_id)",
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': f"Comment {comment_id} marked as CONSUMED."})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        # This error is thrown if the ConditionExpression fails (item doesn't exist)
        print(f"Comment ID {comment_id} not found.")
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f"Comment with ID {comment_id} not found."})
        }
    except Exception as e:
        print(f"Error updating item in DynamoDB: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
