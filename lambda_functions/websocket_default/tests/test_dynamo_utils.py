import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch
import boto3
from botocore.exceptions import ClientError

from src.dynamo_utils import get_previous_chat, store_connection_id, update_conversation

class TestChatStorage(unittest.TestCase):
    def setUp(self):
        self.connection_id = "test_connection_id"
        self.messages = [{"message": "Hello"}, {"message": "How can I help you?"}]
        self.table_name = "test_table"

    @patch('src.dynamo_utils.dynamo_client')
    def test_get_previous_chat(self, mock_dynamo_client):
        mock_response = {
            'Item': {
                'Conversation': {
                    'L': [
                        {'S': '{"message": "hello"}'},
                        {'S': '{"message": "world"}'} 
                    ]
                }
            }
        }
        mock_dynamo_client.get_item.return_value = mock_response
        
        previous_chat = get_previous_chat(self.connection_id)
       
        mock_dynamo_client.get_item.assert_called_with(
            TableName=os.getenv('TABLE_NAME'),
            Key={'ConnectionID': {'S': self.connection_id}}
        )
        self.assertEqual(previous_chat, ['{"message": "hello"}', '{"message": "world"}'])


    @patch('src.dynamo_utils.dynamo_client')
    def test_store_connection_id(self, mock_dynamo_client):
        # Call the function and assert the DynamoDB put_item call
        store_connection_id(self.connection_id)
        mock_dynamo_client.put_item.assert_called_with(
            TableName=os.getenv('TABLE_NAME'),
            Item={'ConnectionID': {'S': self.connection_id}}
        )

    @patch('src.dynamo_utils.dynamo_client')
    def test_update_conversation(self, mock_dynamo_client):

        # Call the function and assert the DynamoDB put_item call
        update_conversation(self.connection_id, self.messages)
        mock_dynamo_client.put_item.assert_called_with(
            TableName=os.getenv('TABLE_NAME'),
            Item={
                'ConnectionID': {"S": self.connection_id},
                'Conversation': {
                    "L": [
                        {"S": '{"message": "Hello"}'},
                        {"S": '{"message": "How can I help you?"}'}
                    ]
                }
            }
        )


if __name__ == '__main__':
    unittest.main()