import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch, MagicMock
import boto3
from botocore.exceptions import ClientError
from jose import jwt
import requests
from src.auth import get_userpool_id, verify_token

class TestTokenVerification(unittest.TestCase):
    def setUp(self):
        self.project_name = "test_project"
        self.region = "eu-central-1"
        self.userpool_id = "test_userpool_id"
        os.environ["PROJECT_NAME"] = self.project_name
        os.environ["REGION"] = self.region

    @patch('boto3.client')
    def test_get_userpool_id(self, mock_cognito_client):
        # Mock the Cognito client
        mock_client = mock_cognito_client.return_value
        mock_client.list_user_pools.return_value = {
            'UserPools': [
                {'Id': self.userpool_id, 'Name': 'Test Pool'}
            ]
        }
        mock_client.describe_user_pool.return_value = {
            'UserPool': {
                'UserPoolTags': {
                    'ProjectName': self.project_name
                }
            }
        }

        # Call the function and assert the result
        userpool_id = get_userpool_id()
        self.assertEqual(userpool_id, self.userpool_id)

    @patch('requests.get')
    def test_verify_token(self, mock_requests_get):
        # Mock the JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "keys": [
                {"kid": "test_kid_1"},
                {"kid": "test_kid_2"}
            ]
        }
        mock_requests_get.return_value = mock_response

        # Create a valid token
        valid_token = jwt.encode({"sub": "test_user"}, "secret_key", algorithm="HS256", headers={"kid": "test_kid_2"})

        # Call the function and assert the result
        self.assertTrue(verify_token({"body": valid_token}))



if __name__ == '__main__':
    unittest.main()