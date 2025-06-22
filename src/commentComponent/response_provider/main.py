import boto3
import os
import json
from decimal import Decimal

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
COMMENTS_TABLE_NAME = os.environ['COMMENTS_TABLE_NAME']

class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert a DynamoDB item's Decimal types to float."""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def handler(event, context):
    """
    This function is triggered by API Gateway.
    It queries DynamoDB for all 'READY' responses and returns them.
    """
    table = dynamodb.Table(COMMENTS_TABLE_NAME)

    try:
        # Query the GSI to get all items with status 'READY'
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('status').eq('READY')
        )
        items = response.get('Items', [])
        
        # Optionally, you could delete the items after reading to prevent re-reading them.
        # This would make the GET endpoint a one-time-read for each response.
        # For now, we'll just return them.

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # CORS header
            },
            'body': json.dumps({'responses': items}, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
