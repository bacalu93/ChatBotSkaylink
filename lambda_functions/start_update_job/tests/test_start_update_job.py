import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):
    @patch('src.lambda_function.boto3.client')
    @patch('src.lambda_function.os.getenv')
    @patch('src.lambda_function.datetime')
    def test_lambda_handler(self, mock_datetime, mock_getenv, mock_boto3_client):
        # Arrange
        mock_datetime.now.return_value = datetime(2023, 5, 1, 12, 0, 0)
        mock_getenv.side_effect = ['my-batch-job-queue', 'my-batch-job-definition']
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        response = lambda_handler({}, {})

        # Assert
        self.assertEqual(response, {
            'statusCode': 200,
            'body': '"Hello from Lambda!"'
        })
        mock_client.submit_job.assert_called_with(
            jobName='update-knowlegdebase-2023-05-01-12-00-00',
            jobQueue='my-batch-job-queue',
            jobDefinition='my-batch-job-definition'
        )

if __name__ == '__main__':
    unittest.main()