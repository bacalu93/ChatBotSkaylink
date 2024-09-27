import json
import boto3
import os
from datetime import datetime

# Initialize boto3 client for DynamoDB
dynamo_client = boto3.client(service_name='dynamodb')
table_name = os.getenv('TABLE_NAME')
s3 = boto3.client('s3')


def upload_file_to_s3(file_path, bucket_name, file_content):
    # Get the current date
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    # Construct the key (path) in S3
    file_name = os.path.basename(file_path)
    s3_key = f"{year}/{month}/{day}/{file_name}"
    
    # Upload the file using put_object
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_content
        )
        print(f"File uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading file: {e}")

def get_previous_chat(connection_id):
    try:
        response = dynamo_client.get_item(
            TableName=table_name,
            Key={'ConnectionID': {'S': connection_id}}
        )
        previous = [json.loads(message.get('S','')) for message in response['Item'].get('Conversation', {}).get('L', [])]
        return previous
    except Exception as e:
        print(f"Error fetching previous chat: {str(e)}")
        return ''

def lambda_handler(event, context):
    print(event)
    connectionId = event["requestContext"]["connectionId"]
    previous_chat_cleaned = [json.dumps(message, ensure_ascii = False) for message in get_previous_chat(connectionId)]
    file_content = '\n'.join(previous_chat_cleaned)
    file_path = f"{connectionId}.txt"
    bucket_name = os.getenv('CHAT_HISTORY_BUCKET')
    if file_content!='':
        upload_file_to_s3(file_path, bucket_name, file_content)


    dynamo_client.delete_item(
            TableName = table_name,
            Key={
                'ConnectionID': {
                    'S': connectionId
                }
            }
        )
    return {
        'statusCode': 200
    }
