import boto3
import os
import json
import urllib.parse
import urllib.request
import time

# By pointing the Lambda's code asset to the 'src' directory,
# we can now directly import from other top-level components.
from writerComponent.main import process_text

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
PROCESSING_TABLE_NAME = os.environ.get('PROCESSING_TABLE_NAME')
WRITER_API_ENDPOINT = os.environ.get('WRITER_API_ENDPOINT', 'https://6676c00ea8d262a60902f23d.mockapi.io/writer')

def handler(event, context):
    """
    This function is triggered by S3, reads the file, calls the Writer service,
    and updates the status in DynamoDB with raw content and processed result.
    """
    print(f"Event: {json.dumps(event)}")
    if not PROCESSING_TABLE_NAME:
        print("Error: PROCESSING_TABLE_NAME environment variable not set.")
        return {'statusCode': 500, 'body': 'Configuration error.'}

    table = dynamodb.Table(PROCESSING_TABLE_NAME)

    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        try:
            # 1. Mark as INITIATED
            print(f"Marking '{file_key}' as INITIATED.")
            table.put_item(
                Item={
                    'file_key': file_key,
                    'status': 'INITIATED',
                    'timestamp': int(time.time()),
                    'last_updated': int(time.time())
                }
            )

            # 2. Extract S3 content
            print(f"Reading content from s3://{bucket_name}/{file_key}")
            file_content = s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read().decode('utf-8')

            # 3. Store raw content
            print(f"Storing raw content for '{file_key}'")
            table.update_item(
                Key={'file_key': file_key},
                UpdateExpression="set #raw = :raw, #lu = :lu",
                ExpressionAttributeNames={
                    '#raw': 'raw',
                    '#lu': 'last_updated'
                },
                ExpressionAttributeValues={
                    ':raw': file_content,
                    ':lu': int(time.time())
                }
            )

            # 4. Call the Writer service
            print(f"Calling Writer service for '{file_key}'")
            writer_result = _call_writer_service(file_content)

            # 5. Mark as READY with result
            print(f"Marking '{file_key}' as READY.")
            table.update_item(
                Key={'file_key': file_key},
                UpdateExpression="set #s = :s, #res = :res, #lu = :lu, #pa = :pa",
                ExpressionAttributeNames={
                    '#s': 'status',
                    '#res': 'result',
                    '#lu': 'last_updated',
                    '#pa': 'processed_at'
                },
                ExpressionAttributeValues={
                    ':s': 'READY',
                    ':res': writer_result,
                    ':lu': int(time.time()),
                    ':pa': int(time.time())
                }
            )
            print(f"Processing complete for '{file_key}'.")

        except Exception as e:
            print(f"Error processing file '{file_key}': {e}")
            table.update_item(
                Key={'file_key': file_key},
                UpdateExpression="set #s = :s, #err = :err, #lu = :lu",
                ExpressionAttributeNames={
                    '#s': 'status',
                    '#err': 'error_message',
                    '#lu': 'last_updated'
                },
                ExpressionAttributeValues={
                    ':s': 'FAILED',
                    ':err': str(e),
                    ':lu': int(time.time())
                }
            )
            raise e

    return {'statusCode': 200, 'body': 'Successfully processed S3 event.'}

def _call_writer_service(file_content):
    # """Calls the Writer service to process the file content using urllib."""
    # try:
    #     # Prepare the request data
    #     data = json.dumps({
    #         "text": file_content,
    #         "context": "file processing"
    #     }).encode('utf-8')
        
    #     # Create the request
    #     req = urllib.request.Request(
    #         WRITER_API_ENDPOINT,
    #         data=data,
    #         headers={
    #             'Content-Type': 'application/json',
    #             'User-Agent': 'S3FileProcessor/1.0'
    #         },
    #         method='POST'
    #     )
        
    #     print(f"Calling Writer service: {WRITER_API_ENDPOINT}")
        
    #     # Make the request
    #     with urllib.request.urlopen(req, timeout=30) as response:
    #         response_data = response.read().decode('utf-8')
    #         result = json.loads(response_data)
    #         processed_text = result.get('result', 'No result received from Writer service.')
    #         print(f"Writer service response: {processed_text}")
    #         return processed_text
        
    # except Exception as e:
    #     print(f"Error calling Writer service: {e}")
        # Fallback to simple processing if Writer service fails
    return f"Imagine a TV that's not just a screen, but a piece of art that elevates your living room. Introducing the Samsung 43-Inch Class Serif QLED 4K Smart TV, where style meets technology. With its sleek and futuristic design, this TV is a statement piece that stands proudly on its own. But it's not just about looks - it's also packed with innovative features like Ambient Mode+, which transforms your TV into a canvas of art and information when you're not watching. Plus, with its standalone smart TV capabilities and voice control, you can enjoy seamless entertainment without the clutter. Whether you're a design enthusiast, a tech lover, or just someone who appreciates the finer things in life, this TV is sure to impress. Get ready to experience the perfect blend of form and function - the Samsung Serif QLED 4K Smart TV, redefining the way you enjoy entertainment." 