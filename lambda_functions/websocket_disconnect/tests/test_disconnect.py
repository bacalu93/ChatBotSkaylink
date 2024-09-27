import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.lambda_function import upload_file_to_s3, get_previous_chat, lambda_handler


class TestLambdaFunction(unittest.TestCase):
    @patch('src.lambda_function.s3')
    @patch('src.lambda_function.datetime')
    def test_upload_file_to_s3(self, mock_datetime, mock_s3):
        # Arrange
        file_path = 'test_file.txt'
        bucket_name = 'test-bucket'
        file_content = b'Test file content'

        mock_datetime.now.return_value = datetime(2023, 4, 20)
        mock_s3.put_object.return_value = {}

        # Act
        upload_file_to_s3(file_path, bucket_name, file_content)

        # Assert
        mock_s3.put_object.assert_called_with(
            Bucket=bucket_name,
            Key='2023/04/20/test_file.txt',
            Body=file_content
        )
    
    @patch('src.lambda_function.dynamo_client')
    def test_get_previous_chat(self, mock_dynamo_client):
        connection_id = 'test-connection-id'
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
        
        previous_chat = get_previous_chat(connection_id)
        
        mock_dynamo_client.get_item.assert_called_with(
            TableName=os.getenv('TABLE_NAME'),
            Key={'ConnectionID': {'S': connection_id}}
        )
        self.assertEqual(previous_chat, [{'message': 'hello'}, {'message': 'world'}])
    
    @patch('src.lambda_function.upload_file_to_s3')
    @patch('src.lambda_function.get_previous_chat')
    @patch('src.lambda_function.dynamo_client')
    def test_lambda_handler(self, mock_dynamo_client, mock_get_previous_chat, mock_upload_file_to_s3):
        event = {
            "requestContext": {
                "connectionId": "test-connection-id"
            }
        }
        
        mock_get_previous_chat.return_value = [{'message': 'hello'}, {'message': 'world'}]
        
        lambda_handler(event, {})
        
        mock_get_previous_chat.assert_called_with('test-connection-id')
        mock_upload_file_to_s3.assert_called_with(
            'test-connection-id.txt',
            os.getenv('CHAT_HISTORY_BUCKET'),
            '{"message": "hello"}\n{"message": "world"}'
        )
        mock_dynamo_client.delete_item.assert_called_with(
            TableName=os.getenv('TABLE_NAME'),
            Key={'ConnectionID': {'S': 'test-connection-id'}}
        )

if __name__ == '__main__':
    unittest.main()