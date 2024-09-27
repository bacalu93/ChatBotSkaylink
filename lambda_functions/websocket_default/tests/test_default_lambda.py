import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock
import boto3

# Add the directory containing the lambda_function.py file to the Python path
here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

# Add the directory containing the lambda_function.py file to the Python path
here = os.path.join(os.path.dirname(__file__), '../src/')
sys.path.append(here)

from lambda_function import handle_authentication, handle_message, get_contexts, create_presigned_urls, lambda_handler
from greeting import greeting

class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        os.environ['WEBSOCKET_URL'] = 'https://example.com'

    @patch('lambda_function.verify_token')
    @patch('lambda_function.websocket_client')
    @patch('lambda_function.store_connection_id')
    def test_handle_authentication(self, mock_store_connection_id, mock_websocket_client, mock_verify_token):
        mock_verify_token.return_value = True
        event_content = {'mode': 'authentication'}
        connection_id = 'abc123'
        response = handle_authentication(event_content, connection_id)
        self.assertEqual(response, {'statusCode': 200, 'body': 'Request successfully finished'})
        mock_websocket_client.post_to_connection.assert_called_once_with(ConnectionId=connection_id, Data=greeting)
        mock_store_connection_id.assert_called_once_with(connection_id)

    @patch('lambda_function.get_previous_chat')
    @patch('lambda_function.update_conversation')
    @patch('lambda_function.brt')
    @patch('lambda_function.websocket_client')
    @patch('lambda_function.create_presigned_urls')
    def test_handle_message(self, mock_create_presigned_urls, mock_websocket_client, mock_brt, mock_update_conversation, mock_get_previous_chat):
        mock_get_previous_chat.return_value = []
        mock_brt.converse_stream.return_value = {'stream': [{'contentBlockDelta': {'delta': {'text': 'Hello, how can I assist you?'}}}]}
        event_content = {'mode': 'message', 'body': 'What is the weather like today?'}
        connection_id = 'abc123'
        response = handle_message(event_content, connection_id)
        self.assertEqual(response, {'statusCode': 200, 'body': 'Request successfully finished'})
        mock_websocket_client.post_to_connection.assert_called()
        mock_update_conversation.assert_called_once_with(connection_id, unittest.mock.ANY)

    @patch('lambda_function.boto3')
    def test_get_contexts(self, mock_boto3):
        with patch('lambda_function.bedrock_agent_runtime_client') as mock_bedrock_agent_runtime_client:
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'mock_kb_id'}}
            mock_boto3.client.return_value = mock_ssm
            mock_bedrock_agent_runtime_client.retrieve.return_value = {
                'retrievalResults': [
                    {
                        'content': {'text': 'This is the first context.'},
                        'location': {'s3Location': {'uri': 's3://bucket/path/to/file.pdf'}},
                        'metadata': {'page_number': 1}
                    },
                    {
                        'content': {'text': 'This is the second context.'},
                        'location': {'s3Location': {'uri': 's3://bucket/path/to/file.pdf'}},
                        'metadata': {'page_number': 2}
                    }
                ]
            }
            add_prompt, source_prefix = get_contexts('What is the weather like today?')
            self.assertIn('The 1. context is:', add_prompt)
            self.assertIn('The 2. context is:', add_prompt)
            self.assertIn('Use inline citations in superscript format, e.g., <sup>1</sup>', add_prompt)
            self.assertEqual(source_prefix, 's3://bucket')

    @patch('lambda_function.boto3')
    def test_create_presigned_urls(self, mock_boto3):
        full_answer = """
        Here is the answer. ¹ Some additional information. ²
    
        Here is the answer.<sup>1</sup> Some additional information.<sup>2</sup>
        ***USED SOURCES:***
        [1] file1.pdf (page 5)
        [2] file2.docx (page 12)
        """
        source_prefix = 's3://bucket/path/to'
        source_string = create_presigned_urls(full_answer, source_prefix)
        self.assertIn('file1.pdf', source_string)
        self.assertIn('file2.docx', source_string)

        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.side_effect = [
            'https://example.com/file1.pdf',
            'https://example.com/file2.docx'
        ]
        mock_boto3.client.return_value = mock_s3_client

        processed_answer = create_presigned_urls(full_answer, source_prefix)

        self.assertIn('[1] file1.pdf (page 5) - <a href="https://example.com/file1.pdf" target="_blank" rel="noopener noreferrer">Link</a>', processed_answer)
        self.assertIn('[2] file2.docx (page 12) - <a href="https://example.com/file2.docx" target="_blank" rel="noopener noreferrer">Link</a>', processed_answer)

    @patch('lambda_function.handle_authentication')
    @patch('lambda_function.handle_message')
    def test_lambda_handler(self, mock_handle_message, mock_handle_authentication):
        mock_handle_authentication.return_value = {'statusCode': 200, 'body': 'Request successfully finished'}
        mock_handle_message.return_value = {'statusCode': 200, 'body': 'Request successfully finished'}

        event = {
            "requestContext": {"connectionId": "abc123"},
            "body": '{"mode": "authentication"}'
        }
        response = lambda_handler(event, {})
        self.assertEqual(response, {'statusCode': 200, 'body': 'Request successfully finished'})

        event = {
            "requestContext": {"connectionId": "abc123"},
            "body": '{"mode": "message", "body": "What is the weather like today?"}'
        }
        response = lambda_handler(event, {})
        self.assertEqual(response, {'statusCode': 200, 'body': 'Request successfully finished'})

if __name__ == '__main__':
    unittest.main()
