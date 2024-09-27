import boto3
import time

def create_knowledge_base(client, kb_name, kb_role_arn, db_name, secret_arn, cluster_arn):
    """Create a knowledge base in Bedrock Agent."""
    return client.create_knowledge_base(
        knowledgeBaseConfiguration={
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': 'arn:aws:bedrock:eu-central-1::foundation-model/cohere.embed-multilingual-v3',
            }
        },
        name=kb_name,
        roleArn=kb_role_arn,
        storageConfiguration={
            'rdsConfiguration': {
                'credentialsSecretArn': secret_arn,
                'databaseName': db_name,
                'fieldMapping': {
                    'metadataField': 'metadata',
                    'primaryKeyField': 'id',
                    'textField': 'chunks',
                    'vectorField': 'embedding'
                },
                'resourceArn': cluster_arn,
                'tableName': 'items'
            },
            'type': 'RDS'
        }
    )

def update_knowledge_base(client, kb_name, kb_role_arn, db_name, secret_arn, cluster_arn, kb_id):
    """Update a knowledge base in Bedrock Agent."""
    return client.update_knowledge_base(
        knowledgeBaseConfiguration={
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': 'arn:aws:bedrock:eu-central-1::foundation-model/cohere.embed-multilingual-v3',
            }
        },
        knowledgeBaseId=kb_id,
        name=kb_name,
        roleArn=kb_role_arn,
        storageConfiguration={
            'rdsConfiguration': {
                'credentialsSecretArn': secret_arn,
                'databaseName': db_name,
                'fieldMapping': {
                    'metadataField': 'metadata',
                    'primaryKeyField': 'id',
                    'textField': 'chunks',
                    'vectorField': 'embedding'
                },
                'resourceArn': cluster_arn,
                'tableName': 'items'
            },
            'type': 'RDS'
        }
    )

def create_data_source(client, kb_id, bucket_arn):
    """Create a data source in Bedrock Agent."""
    return client.create_data_source(
        dataSourceConfiguration={
            's3Configuration': {
                'bucketArn': bucket_arn
            },
            'type': 'S3'
        },
        knowledgeBaseId=kb_id,
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

def update_data_source(client, kb_id, bucket_arn, ds_id):
    """Update a data source in Bedrock Agent."""
    return client.update_data_source(
        dataSourceConfiguration={
            's3Configuration': {
                'bucketArn': bucket_arn
            },
            'type': 'S3'
        },
        dataSourceId=ds_id,
        knowledgeBaseId=kb_id,
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

def wait_for_knowledge_base_creation(client, kb_id):
    """Wait for the knowledge base creation to complete."""
    response = client.get_knowledge_base(knowledgeBaseId=kb_id)
    while response['knowledgeBase']['status'] == "CREATING" or response['knowledgeBase']['status'] == "UPDATING":
        time.sleep(5)
        response = client.get_knowledge_base(knowledgeBaseId=kb_id)
    return response


def start_ingestion_job(client, ds_id, kb_id):
    """Start the ingestion job."""
    return client.start_ingestion_job(
        dataSourceId=ds_id,
        knowledgeBaseId=kb_id
    )