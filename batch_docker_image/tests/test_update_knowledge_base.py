import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)
import unittest
from unittest.mock import patch, MagicMock, call
import boto3
import json
from database import setup_database_connection, create_database_schema
from bedrock import create_knowledge_base, update_knowledge_base, create_data_source, update_data_source, wait_for_knowledge_base_creation, start_ingestion_job
from file_processing import process_file
from update_knowledge_base import get_secret, main

class TestMain(unittest.TestCase):
    @patch.dict(os.environ, {
        'SECRET_ARN': 'secret_arn',
        'REGION': 'us-east-1',
        'KB_NAME': 'test_kb',
        'KB_ROLE_ARN': 'kb_role_arn',
        'DB_NAME': 'test_db',
        'CLUSTER_ARN': 'cluster_arn',
        'KB_BUCKET_ARN': 'bucket_arn',
        'KB_BUCKET_NAME': 'bucket_name'
    })
    @patch('update_knowledge_base.boto3.session.Session')
    @patch('update_knowledge_base.boto3.client')
    @patch('update_knowledge_base.boto3.resource')
    @patch('update_knowledge_base.setup_database_connection')
    @patch('update_knowledge_base.create_database_schema')
    @patch('update_knowledge_base.create_knowledge_base')
    @patch('update_knowledge_base.update_knowledge_base')
    @patch('update_knowledge_base.create_data_source')
    @patch('update_knowledge_base.update_data_source')
    @patch('update_knowledge_base.wait_for_knowledge_base_creation')
    @patch('update_knowledge_base.start_ingestion_job')
    @patch('update_knowledge_base.process_file')
    @patch('update_knowledge_base.get_secret')
    def test_main(self, mock_get_secret, mock_process_file, mock_start_ingestion_job, mock_wait_for_knowledge_base_creation, mock_update_data_source, mock_create_data_source, mock_update_knowledge_base, mock_create_knowledge_base, mock_create_database_schema, mock_setup_database_connection, mock_boto3_resource, mock_boto3_client, mock_boto3_session):
        mock_boto3_session.return_value.client.return_value = MagicMock()
        mock_setup_database_connection.return_value = MagicMock()
        mock_create_knowledge_base.return_value = {'knowledgeBase': {'knowledgeBaseId': 'test_kb_id'}}
        mock_create_data_source.return_value = {'dataSource': {'dataSourceId': 'test_ds_id'}}
        mock_get_secret.return_value = '{"db_user": "test_user", "db_password": "test_password"}'
        mock_process_file.return_value = ([], [], [], [])

        # Mock the S3 client response
        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'test.pdf'},
                {'Key': 'test.docx'},
                {'Key': 'test.txt'}
            ]
        }

        # Mock the S3 objects
        mock_s3_objects = [
            mock_boto3_resource.return_value.Object('bucket_name', 'test.pdf'),
            mock_boto3_resource.return_value.Object('bucket_name', 'test.docx'),
            mock_boto3_resource.return_value.Object('bucket_name', 'test.txt')
        ]
        mock_s3 = mock_boto3_resource.return_value.Bucket('bucket_name')
        mock_s3.objects.filter.return_value = mock_s3_objects

        main()

        mock_setup_database_connection.assert_called_once_with(json.loads(mock_get_secret.return_value))
        mock_create_database_schema.assert_called_once_with(mock_setup_database_connection.return_value)
        mock_create_knowledge_base.assert_called_once_with(mock_boto3_client.return_value, 'test_kb', 'kb_role_arn', 'test_db', 'secret_arn', 'cluster_arn')
        mock_update_knowledge_base.assert_not_called()
        mock_create_data_source.assert_called_once_with(mock_boto3_client.return_value, 'test_kb_id', 'bucket_arn')
        mock_update_data_source.assert_not_called()
        mock_wait_for_knowledge_base_creation.assert_called_once_with(mock_boto3_client.return_value, 'test_kb_id')
        mock_start_ingestion_job.assert_not_called()
        mock_process_file.assert_has_calls([
            call('test.pdf', 'bucket_name', mock_s3_client, [], [], [], []),
            call('test.docx', 'bucket_name', mock_s3_client, [], [], [], []),
            call('test.txt', 'bucket_name', mock_s3_client, [], [], [], [])
        ])


    @patch('boto3.session.Session')
    @patch('boto3.client')
    def test_get_secret(self, mock_boto3_client, mock_boto3_session):
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {'SecretString': '{"key": "value"}'}
        mock_boto3_session.return_value.client.return_value = mock_client

        secret = get_secret('secret_arn', 'eu-central-1')
        print(f"Secret value: {secret}")

        self.assertEqual(secret, '{"key": "value"}')

if __name__ == '__main__':
    unittest.main()