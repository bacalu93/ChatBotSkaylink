import os
import sys
# Add the parent directory to the system path
here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)
import unittest
from unittest.mock import patch, MagicMock
from botocore.response import StreamingBody
from embedding import calculate_document_embeddings
class TestCalculateDocumentEmbeddings(unittest.TestCase):
    @patch('embedding.boto3.client')
    def test_calculate_document_embeddings(self, mock_client):
        # Mock the Bedrock client
        mock_bedrock_client = MagicMock()
        mock_client.return_value = mock_bedrock_client
        # Mock the response from the Bedrock client
        mock_streaming_body = MagicMock(spec=StreamingBody)
        mock_streaming_body.read.return_value = '{"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]}'.encode()
        mock_response = {
            "body": mock_streaming_body
        }
        mock_bedrock_client.invoke_model.return_value = mock_response
        # Call the function with a sample list of documents
        documents = ["This is the first document.", "This is the second document."]
        embeddings = calculate_document_embeddings(documents)
        # Assert the expected behavior
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        # Verify the Bedrock client was called with the expected arguments
        mock_bedrock_client.invoke_model.assert_called_once_with(
            accept="application/json",
            contentType="application/json",
            body='{"texts": ["This is the first document.", "This is the second document."], "input_type": "search_document"}',
            modelId="cohere.embed-multilingual-v3"
        )
    @patch('embedding.boto3.client')
    def test_calculate_document_embeddings_with_batching(self, mock_client):
        # Mock the Bedrock client
        mock_bedrock_client = MagicMock()
        mock_client.return_value = mock_bedrock_client

        # Mock the responses from the Bedrock client
        mock_streaming_body_1 = MagicMock(spec=StreamingBody)
        mock_streaming_body_1.read.return_value = '{"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], [0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]}'.encode()
        mock_streaming_body_2 = MagicMock(spec=StreamingBody)
        mock_streaming_body_2.read.return_value = '{"embeddings": [[0.7, 0.8, 0.9]]}'.encode()
        mock_responses = [
            {"body": mock_streaming_body_1},
            {"body": mock_streaming_body_2}
        ]
        mock_bedrock_client.invoke_model.side_effect = mock_responses

        # Call the function with a sample list of documents
        documents = ["This is the first document.", "This is the second document.", "This is the third document.", "This is the fourth document.", "This is the fifth document.", "This is the sixth document."]
        embeddings = calculate_document_embeddings(documents)

        # Assert the expected behavior
        self.assertEqual(len(embeddings), 6)
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], [0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])

        # Verify the Bedrock client was called with the expected arguments
        self.assertEqual(mock_bedrock_client.invoke_model.call_count, 2)
        mock_bedrock_client.invoke_model.assert_any_call(
            accept="application/json",
            contentType="application/json",
            body='{"texts": ["This is the first document.", "This is the second document.", "This is the third document.", "This is the fourth document.", "This is the fifth document."], "input_type": "search_document"}',
            modelId="cohere.embed-multilingual-v3"
        )
        mock_bedrock_client.invoke_model.assert_any_call(
            accept="application/json",
            contentType="application/json",
            body='{"texts": ["This is the sixth document."], "input_type": "search_document"}',
            modelId="cohere.embed-multilingual-v3"
        )
