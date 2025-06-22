import boto3
import os
import json
from decimal import Decimal

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
PROCESSING_TABLE_NAME = os.environ['PROCESSING_TABLE_NAME']

def handler(event, context):
    """
    This function is triggered by a GET request to /file-status.
    It checks the file processing status table and returns results for files that are ready.
    """
    try:
        # Get all items from the file processing status table
        table = dynamodb.Table(PROCESSING_TABLE_NAME)
        
        # Scan the table to get all items
        response = table.scan()
        items = response.get('Items', [])
        
        # Filter for files that are ready and return their results
        ready_results = []
        for item in items:
            status = item.get('status', '')
            if status == 'READY':
                result = item.get('result', '')
                raw = item.get('raw', '')
                if result:  # Only include if there's actually a result
                    ready_results.append({'result': result, 'raw': raw})
        
        print(f"Found {len(ready_results)} ready results out of {len(items)} total files")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'results': ready_results,
                'count': len(ready_results)
            })
        }

    except Exception as e:
        print(f"Error checking file status: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def _convert_decimal(obj):
    """Convert Decimal objects to regular Python types for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj 