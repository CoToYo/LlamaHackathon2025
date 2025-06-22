import boto3
import os
import json
import time
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
COMMENTS_TABLE_NAME = os.environ['COMMENTS_TABLE_NAME']
WRITER_API_ENDPOINT = os.environ.get('WRITER_API_ENDPOINT', 'https://6676c00ea8d262a60902f23d.mockapi.io/writer')

# LLAMA API configuration
LLAMA_API_KEY = os.environ.get("LLAMA_API_KEY")
LLAMA_API_URL = "https://api.llama.com/v1/chat/completions"

def handler(event, context):
    """
    This function is triggered by SQS with a batch of comments.
    It orchestrates a stateful, multi-step process to filter, select,
    and get answers for user questions.
    """
    # 1. Extract comments from the SQS batch
    new_comments = _extract_comments_from_event(event)
    if not new_comments:
        print("No new comments to process.")
        return {'statusCode': 200, 'body': 'Empty event.'}
    
    # 2. Get the history of already processed questions
    processed_questions = _get_processed_questions_log()
    
    # 3. Use Llama to select new, unique questions from the batch
    selected_questions = _select_new_questions_with_llama(new_comments, processed_questions)
    if not selected_questions:
        print("LLM selected no new questions to process.")
        return {'statusCode': 200, 'body': 'No new questions selected.'}

    # 4. Immediately store new questions with "INITIATED" status
    initiated_items = _store_initiated_questions(selected_questions)

    # 5. Update the central log with the newly processed questions
    _update_processed_questions_log(processed_questions, selected_questions)

    # 6. Get answers from the Writer service in parallel
    _get_answers_and_update_status(initiated_items)
    
    print("Batch processing complete.")
    return {'statusCode': 200, 'body': 'Batch processed successfully.'}

def _extract_comments_from_event(event):
    """Extracts and performs exact-match deduplication on comments from SQS records."""
    comments = set()
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            comments.add(message_body.get('text', ''))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Skipping malformed record: {record.get('messageId', '')}, error: {e}")
    return list(filter(None, comments))

def _get_processed_questions_log():
    """Retrieves the list of previously processed questions from DynamoDB."""
    try:
        response = dynamodb.Table(COMMENTS_TABLE_NAME).get_item(Key={'comment_id': "processed_questions_log"})
        return response.get('Item', {}).get('questions', [])
    except Exception as e:
        print(f"Could not read question log, starting fresh. Error: {e}")
        return []

def _select_new_questions_with_llama(new_comments, processed_questions):
    """Builds a prompt and calls the Llama API to get a list of new, unique questions."""
    prompt = _build_llama_prompt(new_comments, processed_questions)
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {LLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": messages
    }
    
    try:
        print(f"Calling LLAMA API at: {LLAMA_API_URL}")
        print(f"Model: Llama-4-Maverick-17B-128E-Instruct-FP8")
        print(f"Messages: {json.dumps(messages, indent=2)}")
        
        response = requests.post(LLAMA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"LLAMA API response: {json.dumps(result, indent=2)}")
        
        if result and 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"LLAMA API content: {content}")
            
            # Robustly parse the JSON from the response string
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_response = json.loads(content[json_start:json_end])
                return json_response.get("newly_selected_questions", [])
            else:
                print("No valid JSON found in LLAMA response")
                return []
        elif result and 'completion_message' in result:
            # Handle LLAMA API specific response format
            completion_message = result['completion_message']
            if 'content' in completion_message and 'text' in completion_message['content']:
                content = completion_message['content']['text']
                print(f"LLAMA API content (completion_message): {content}")
                
                # Robustly parse the JSON from the response string
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_response = json.loads(content[json_start:json_end])
                    return json_response.get("newly_selected_questions", [])
                else:
                    print("No valid JSON found in LLAMA response")
                    return []
            else:
                print("Invalid completion_message format")
                return []
        else:
            print("Invalid response format from LLAMA API")
            return []

    except Exception as e:
        print(f"Error calling LLAMA API: {e}")
        raise e

def _build_llama_prompt(new_comments, processed_questions):
    """Creates the detailed prompt for the LLM."""
    # Using f-strings for cleaner multi-line string formatting
    return f"""
You are an AI assistant for a live shopping stream. Your task is to analyze a batch of NEW user comments in the context of questions that have ALREADY been asked, and select only the truly NEW, representative, product-related questions.

CONTEXT:
Here is the list of questions that have already been selected and asked previously. Do NOT select these questions again or any minor variations of them:
---
{json.dumps(processed_questions, indent=2)}
---

TASK:
Now, analyze this NEW batch of user comments. Identify important, new product questions that are NOT semantically similar to the ones in the context list above.
---
NEW BATCH:
{json.dumps(new_comments, indent=2)}
---

Please perform the following steps:
1. From the NEW BATCH, identify direct product questions.
2. Compare them against the list of previously asked questions to ensure they are genuinely new topics.
3. Group any similar new questions and pick the single best one.
4. Return a JSON object with a single key "newly_selected_questions", which is a list of the new representative question strings you have chosen. The list should contain at most 5 questions.

Example output format:
{{
  "newly_selected_questions": [
    "What material is it made of?",
    "How long does shipping take?"
  ]
}}
"""

def _store_initiated_questions(questions):
    """Stores a list of questions in DynamoDB with 'INITIATED' status."""
    initiated_items = []
    print(f"Storing {len(questions)} questions with status INITIATED.")
    with dynamodb.Table(COMMENTS_TABLE_NAME).batch_writer() as batch:
        for q_text in questions:
            item = {
                'comment_id': f"question-{uuid.uuid4()}",
                'question': q_text,
                'status': 'INITIATED',
                'timestamp': int(time.time())
            }
            batch.put_item(Item=item)
            initiated_items.append(item)
    return initiated_items

def _get_answers_and_update_status(items_to_process):
    """Uses a thread pool to get answers for questions and update their status in DynamoDB."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map each item to the _get_and_update_single_answer function
        # This will run the function for each item in a separate thread
        executor.map(_get_and_update_single_answer, items_to_process)

def _get_latest_raw_data_from_ddb():
    """Fetch the latest 'raw' field with status=READY from FileProcessingStatusTable."""
    table_name = "AiLiveStreamStack-FileProcessingStatusTable3F2FBEB5-1GF7R4CV0YJ15"
    table = boto3.resource('dynamodb').Table(table_name)
    try:
        response = table.scan()
        items = response.get('Items', [])
        # Only keep items with status=READY and non-empty raw, sort by processed_at/timestamp descending
        ready_items = [item for item in items if item.get('status') == 'READY' and item.get('raw')]
        if not ready_items:
            print("No READY raw data found in FileProcessingStatusTable.")
            return None
        ready_items.sort(key=lambda x: x.get('processed_at', x.get('timestamp', 0)), reverse=True)
        return ready_items[0]['raw']
    except Exception as e:
        print(f"Error fetching raw data from FileProcessingStatusTable: {e}")
        return None

def _get_and_update_single_answer(item):
    """Generate answer using Llama and update the main table."""
    table = dynamodb.Table(COMMENTS_TABLE_NAME)
    question = item['question']
    comment_id = item['comment_id']
    try:
        # 1. Fetch latest raw data
        raw_data = _get_latest_raw_data_from_ddb()
        if not raw_data:
            print("No raw data available, skipping answer generation.")
            answer = "(No product info available, cannot answer.)"
        else:
            # 2. Build English prompt
            prompt = f"""
You are an AI assistant for a live shopping stream. Based on the following product information and the user's question, generate a concise and professional answer.\n\nProduct Information:\n{raw_data}\n\nUser Question:\n{question}\n\nPlease output only the answer text.
"""
            # 3. Call Llama API
            headers = {
                "Authorization": f"Bearer {LLAMA_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            try:
                response = requests.post(LLAMA_API_URL, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                print(f"LLAMA answer API response: {json.dumps(result, ensure_ascii=False)}")
                answer = None
                if result and 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content'].strip()
                elif result and 'completion_message' in result:
                    cm = result['completion_message']
                    if 'content' in cm and isinstance(cm['content'], dict) and 'text' in cm['content']:
                        answer = cm['content']['text'].strip()
                if not answer:
                    answer = "(No valid answer received.)"
            except Exception as e:
                print(f"Error calling LLAMA for answer: {e}")
                answer = "(AI API error, unable to generate answer.)"
        # 4. Update main table
        table.update_item(
            Key={'comment_id': comment_id},
            UpdateExpression="SET #s = :s, #a = :a",
            ExpressionAttributeNames={"#s": "status", "#a": "answer"},
            ExpressionAttributeValues={":s": "READY", ":a": answer}
        )
        print(f"Updated {comment_id} to READY with answer: {answer}")
    except Exception as e:
        print(f"Failed to process question {comment_id}: {e}")

def _update_processed_questions_log(old_log, new_questions):
    """Appends new questions to the processed questions log in DynamoDB."""
    print(f"Updating question log with {len(new_questions)} new questions.")
    new_log = old_log + new_questions
    try:
        dynamodb.Table(COMMENTS_TABLE_NAME).put_item(
            Item={
                'comment_id': "processed_questions_log",
                'questions': new_log
            }
        )
    except Exception as e:
        print(f"CRITICAL: Failed to update processed questions log! Error: {e}")
