import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch, MagicMock
from bedrock import (
    create_knowledge_base,
    update_knowledge_base,
    create_data_source,
    update_data_source,
    wait_for_knowledge_base_creation,
    start_ingestion_job
)

class TestBedrockAgent(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()

    @patch('bedrock.boto3.client')
    def test_create_knowledge_base(self, mock_client):
        mock_client.return_value = self.client
        create_knowledge_base(
            self.client, 'test_kb', 'arn:aws:iam::123456789012:role/test-role',
            'test_db', 'arn:aws:secretsmanager:eu-central-1:123456789012:secret:test-secret',
            'arn:aws:rds:eu-central-1:123456789012:cluster:test-cluster'
        )
        self.client.create_knowledge_base.assert_called_once_with(
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:eu-central-1::foundation-model/cohere.embed-multilingual-v3',
                }
            },
            name='test_kb',
            roleArn='arn:aws:iam::123456789012:role/test-role',
            storageConfiguration={
                'rdsConfiguration': {
                    'credentialsSecretArn': 'arn:aws:secretsmanager:eu-central-1:123456789012:secret:test-secret',
                    'databaseName': 'test_db',
                    'fieldMapping': {
                        'metadataField': 'metadata',
                        'primaryKeyField': 'id',
                        'textField': 'chunks',
                        'vectorField': 'embedding'
                    },
                    'resourceArn': 'arn:aws:rds:eu-central-1:123456789012:cluster:test-cluster',
                    'tableName': 'items'
                },
                'type': 'RDS'
            }
        )

    @patch('bedrock.boto3.client')
    def test_update_knowledge_base(self, mock_client):
        mock_client.return_value = self.client
        update_knowledge_base(
            self.client, 'test_kb', 'arn:aws:iam::123456789012:role/test-role',
            'test_db', 'arn:aws:secretsmanager:eu-central-1:123456789012:secret:test-secret',
            'arn:aws:rds:eu-central-1:123456789012:cluster:test-cluster', 'kb-123'
        )
        self.client.update_knowledge_base.assert_called_once_with(
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:eu-central-1::foundation-model/cohere.embed-multilingual-v3',
                }
            },
            knowledgeBaseId='kb-123',
            name='test_kb',
            roleArn='arn:aws:iam::123456789012:role/test-role',
            storageConfiguration={
                'rdsConfiguration': {
                    'credentialsSecretArn': 'arn:aws:secretsmanager:eu-central-1:123456789012:secret:test-secret',
                    'databaseName': 'test_db',
                    'fieldMapping': {
                        'metadataField': 'metadata',
                        'primaryKeyField': 'id',
                        'textField': 'chunks',
                        'vectorField': 'embedding'
                    },
                    'resourceArn': 'arn:aws:rds:eu-central-1:123456789012:cluster:test-cluster',
                    'tableName': 'items'
                },
                'type': 'RDS'
            }
        )

    @patch('bedrock.boto3.client')
    def test_create_data_source(self, mock_client):
        mock_client.return_value = self.client
        create_data_source(self.client, 'kb-123', 'arn:aws:s3:::test-bucket')
        self.client.create_data_source.assert_called_once_with(
            dataSourceConfiguration={
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::test-bucket'
                },
                'type': 'S3'
            },
            knowledgeBaseId='kb-123',
            name='datasource_kb',
            vectorIngestionConfiguration={
                'chunkingConfiguration': {
                    'chunkingStrategy': 'FIXED_SIZE',
                    'fixedSizeChunkingConfiguration': {
                        'maxTokens': 512,
                        'overlapPercentage': 15
                    }
                }
            }
        )

    @patch('bedrock.boto3.client')
    def test_update_data_source(self, mock_client):
        mock_client.return_value = self.client
        update_data_source(self.client, 'kb-123', 'arn:aws:s3:::test-bucket', 'ds-123')
        self.client.update_data_source.assert_called_once_with(
            dataSourceConfiguration={
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::test-bucket'
                },
                'type': 'S3'
            },
            dataSourceId='ds-123',
            knowledgeBaseId='kb-123',
            name='datasource_kb',
            vectorIngestionConfiguration={
                'chunkingConfiguration': {
                    'chunkingStrategy': 'FIXED_SIZE',
                    'fixedSizeChunkingConfiguration': {
                        'maxTokens': 512,
                        'overlapPercentage': 15
                    }
                }
            }
        )

    @patch('bedrock.boto3.client')
    @patch('bedrock.time.sleep')
    def test_wait_for_knowledge_base_creation(self, mock_sleep, mock_client):
        mock_client.return_value = self.client
        self.client.get_knowledge_base.side_effect = [
            {'knowledgeBase': {'status': 'CREATING'}},
            {'knowledgeBase': {'status': 'CREATING'}},
            {'knowledgeBase': {'status': 'ACTIVE'}}
        ]
        wait_for_knowledge_base_creation(self.client, 'kb-123')
        self.assertEqual(self.client.get_knowledge_base.call_count, 3)
        mock_sleep.assert_called_with(5)

    @patch('bedrock.boto3.client')
    def test_start_ingestion_job(self, mock_client):
        mock_client.return_value = self.client
        start_ingestion_job(self.client, 'ds-123', 'kb-123')
        self.client.start_ingestion_job.assert_called_once_with(
            dataSourceId='ds-123',
            knowledgeBaseId='kb-123'
        )