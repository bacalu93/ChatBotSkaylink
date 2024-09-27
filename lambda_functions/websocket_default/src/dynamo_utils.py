import boto3
import os
import json
# Initialize boto3 client for DynamoDB
dynamo_client = boto3.client(service_name='dynamodb')
table_name = os.getenv('TABLE_NAME')

def get_previous_chat(connection_id):
    try:
        response = dynamo_client.get_item(
            TableName=table_name,
            Key={'ConnectionID': {'S': connection_id}}
        )
        previous = [message.get('S','') for message in response['Item'].get('Conversation', {}).get('L', [])]
        return previous
    except Exception as e:
        print(f"Error fetching previous chat: {str(e)}")
        return ''

def store_connection_id(connection_id):
    try:
        dynamo_client.put_item(
            TableName=table_name,
            Item={'ConnectionID': {'S': connection_id}}
        )
    except Exception as e:
        print(f"Error storing connection ID: {str(e)}")

def update_conversation(connection_id, messages):
    try:
        message_dicts = [{"S" : json.dumps(message)} for message in messages]
        dynamo_client.put_item(
            TableName=table_name,
            Item={
                'ConnectionID': {"S": connection_id},
                'Conversation': {
                                    "L": message_dicts
                                  }
            }
        )
    except Exception as e:
        print(f"Error updating conversation: {str(e)}")