import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from botocore.response import StreamingBody
from unittest.mock import patch, MagicMock
from file_processing import process_file
from pypdf import PdfReader

class TestProcessFile(unittest.TestCase):
    @patch('file_processing.boto3.client')
    @patch('file_processing.uuid.uuid4')
    @patch('file_processing.os.path.join')
    @patch('file_processing.PdfReader')
    @patch('file_processing.partition_pdf')
    @patch('file_processing.partition_docx')
    @patch('file_processing.partition_text')
    @patch('file_processing.calculate_document_embeddings')
    def test_process_pdf_file(self, mock_calculate_embeddings, mock_partition_text, mock_partition_docx, mock_partition_pdf, mock_pdf_reader, mock_join, mock_uuid, mock_client):
        # Mock the S3 client
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client


        # Mock the uuid.uuid4() function to return a predictable value
        mock_uuid.return_value = 'test-uuid'

        # Mock the os.path.join function to return the expected file path
        mock_join.return_value = '/tmp/test-uuid.pdf'

        # Mock the PDF reader
        mock_pdf_reader_instance = MagicMock(spec=PdfReader)
        mock_pdf_reader_instance.page_labels = ['x', '1', '2']
        mock_pdf_reader.return_value = mock_pdf_reader_instance

        mock_partition_pdf.return_value = [
            MagicMock(metadata=MagicMock(page_number='1'), __str__=lambda self: "This is the first paragraph."),
            MagicMock(metadata=MagicMock(page_number='2'), __str__=lambda self: "This is the second paragraph."),
            MagicMock(metadata=MagicMock(page_number='3'), __str__=lambda self: "This is the third paragraph.")
        ]

        # Mock the embeddings calculation
        mock_calculate_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_streaming_body = MagicMock(spec=StreamingBody)
        mock_streaming_body.read.return_value = '{"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]}'.encode()

        # Call the function with a PDF file
        contents = []
        page_numbers = []
        sources = []
        embeddings = []
        process_file('test.pdf', 'test-bucket', mock_s3_client, contents, page_numbers, sources, embeddings)
        print(contents)
        print(page_numbers)

        # Assert the expected behavior
        self.assertEqual(len(contents), 3)
        self.assertEqual(page_numbers, ['x', '1', '2'])
        self.assertEqual(len(sources), 3)
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])

        # Verify the S3 client was called with the expected arguments
        mock_s3_client.get_object.assert_called_once_with(Bucket='test-bucket', Key='test.pdf')
        mock_s3_client.download_file.assert_called_once_with('test-bucket', 'test.pdf', '/tmp/test-uuid.pdf')

        # Verify the partition_pdf function was called with the expected arguments
        mock_partition_pdf.assert_called_once_with('/tmp/test-uuid.pdf', strategy='auto', chunking_strategy='by_title')

        # Verify the calculate_document_embeddings function was called with the expected arguments
        mock_calculate_embeddings.assert_called_once_with(['This is the first paragraph.', 'This is the second paragraph.', 'This is the third paragraph.'])


    @patch('file_processing.boto3.client')
    @patch('file_processing.uuid.uuid4')
    @patch('file_processing.partition_pdf')
    @patch('file_processing.partition_docx')
    @patch('file_processing.partition_text')
    @patch('file_processing.calculate_document_embeddings')
    def test_process_docx_file(self, mock_calculate_embeddings, mock_partition_text, mock_partition_docx, mock_partition_pdf, mock_uuid, mock_client):
        # Mock the S3 client
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client

        # Mock the uuid.uuid4() function to return a predictable value
        mock_uuid.return_value = 'test-uuid'

        # Mock the DOCX partitioning
        mock_partition_docx.return_value = [
            MagicMock(metadata=MagicMock(page_number='1'), __str__=lambda self: "This is the first paragraph."),
            MagicMock(metadata=MagicMock(page_number='2'), __str__=lambda self: "This is the second paragraph.")
        ]

        # Mock the embeddings calculation
        mock_calculate_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        # Call the function with a DOCX file
        contents = []
        page_numbers = []
        sources = []
        embeddings = []
        process_file('test.docx', 'test-bucket', mock_s3_client, contents, page_numbers, sources, embeddings)

        # Assert the expected behavior
        self.assertEqual(len(contents), 2)
        self.assertEqual(contents, ["This is the first paragraph.", "This is the second paragraph."])
        self.assertEqual(page_numbers, ['1', '2'])
        self.assertEqual(len(sources), 2)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Verify the S3 client was called with the expected arguments
        mock_s3_client.get_object.assert_called_once_with(Bucket='test-bucket', Key='test.docx')
        mock_s3_client.download_file.assert_called_once_with('test-bucket', 'test.docx', '/tmp/test-uuid.docx')

        # Verify the partition_docx function was called with the expected arguments
        mock_partition_docx.assert_called_once_with('/tmp/test-uuid.docx', strategy='auto', chunking_strategy='by_title')

        # Verify the calculate_document_embeddings function was called with the expected arguments
        mock_calculate_embeddings.assert_called_once_with(["This is the first paragraph.", "This is the second paragraph."])


    @patch('file_processing.boto3.client')
    @patch('file_processing.uuid.uuid4')
    @patch('file_processing.partition_pdf')
    @patch('file_processing.partition_docx')
    @patch('file_processing.partition_text')
    @patch('file_processing.calculate_document_embeddings')
    def test_process_txt_file(self, mock_calculate_embeddings, mock_partition_text, mock_partition_docx, mock_partition_pdf, mock_uuid, mock_client):
        # Mock the S3 client
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client


        # Mock the uuid.uuid4() function to return a predictable value
        mock_uuid.return_value = 'test-uuid'

        # Mock the text partitioning
        mock_partition_text.return_value = [
            "This is the first paragraph.",
            "This is the second paragraph.",
            "This is the third paragraph."
        ]

        # Mock the embeddings calculation
        mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_calculate_embeddings.return_value = mock_embeddings
        mock_streaming_body = MagicMock(spec=StreamingBody)
        mock_streaming_body.read.return_value = '{"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]}'.encode()

        # Call the function with a .txt file
        contents = []
        page_numbers = []
        sources = []
        embeddings = []
        process_file('test.txt', 'test-bucket', mock_s3_client, contents, page_numbers, sources, embeddings)

        # Assert the expected behavior
        self.assertEqual(len(contents), 3)
        self.assertEqual(page_numbers, ['1', '1', '1'])
        self.assertEqual(len(sources), 3)
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(embeddings, mock_embeddings)

        # Verify the S3 client was called with the expected arguments
        mock_s3_client.get_object.assert_called_once_with(Bucket='test-bucket', Key='test.txt')
        mock_s3_client.download_file.assert_called_once_with('test-bucket', 'test.txt', '/tmp/test-uuid.txt')

        # Verify the partition_text function was called with the expected arguments
        mock_partition_text.assert_called_once_with('/tmp/test-uuid.txt', chunking_strategy='by_title')

        # Verify the calculate_document_embeddings function was called with the expected arguments
        mock_calculate_embeddings.assert_called_once_with(['This is the first paragraph.', 'This is the second paragraph.', 'This is the third paragraph.'])
