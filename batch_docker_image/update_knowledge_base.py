import os
import boto3
import uuid
import json
import time
from database import setup_database_connection, create_database_schema
from bedrock import create_knowledge_base, update_knowledge_base, create_data_source, update_data_source, wait_for_knowledge_base_creation, start_ingestion_job
from file_processing import process_file

def get_secret(secret_name, region_name):
    """Retrieve a secret from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return get_secret_value_response['SecretString']
    except ClientError as e:
        raise e


def main():

    secret_arn = os.getenv('SECRET_ARN')
    region = os.getenv('REGION')
    kb_name = os.getenv('KB_NAME')
    kb_role_arn = os.getenv('KB_ROLE_ARN')
    db_name = os.getenv('DB_NAME')
    cluster_arn = os.getenv('CLUSTER_ARN')
    bucket_arn = os.getenv('KB_BUCKET_ARN')
    bucket_name = os.getenv('KB_BUCKET_NAME')

    secret = json.loads(get_secret(secret_arn, region))
    conn = setup_database_connection(secret)
    create_database_schema(conn)

    ssm = boto3.client('ssm')
    client = boto3.client('bedrock-agent')
    try:
        kb_response = create_knowledge_base(client, kb_name, kb_role_arn, db_name, secret_arn, cluster_arn)
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        ssm.put_parameter(Name='knowledgebase_id', Value=kb_id, Type='String')
        ds_response = create_data_source(client, kb_id, bucket_arn)
        ds_id = ds_response['dataSource']['dataSourceId']
        ssm.put_parameter(Name='datasource_id', Value=ds_id, Type='String')
    except client.exceptions.ConflictException:
        try:
            kb_id=ssm.get_parameter(Name='knowledgebase_id')['Parameter']['Value']
            kb_response = update_knowledge_base(client, kb_name, kb_role_arn, db_name, secret_arn, cluster_arn, kb_id)
            ds_id=ssm.get_parameter(Name='datasource_id')['Parameter']['Value']
            kb_response = update_data_source(client, kb_id, bucket_arn, ds_id)
        except Exception:
            pass

    wait_for_knowledge_base_creation(client, kb_id)

    try:
        with conn.cursor() as cursor:
            delete_query = "DELETE FROM items"
            cursor.execute(delete_query)

            s3_client = boto3.client('s3')
            response = s3_client.list_objects_v2(
                Bucket=bucket_name
            )
            os.makedirs('tmp', exist_ok=True)
            embeddings = []
            page_numbers = []
            contents = []
            sources = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    file_key = obj['Key']
                    print(f"Reading file: {file_key}")

                    contents, page_numbers, sources, embeddings = process_file(file_key, bucket_name, s3_client, contents, page_numbers, sources, embeddings)   
                    insert_query = f"INSERT INTO items (id, chunks, metadata, embedding, page_number) VALUES (%s, %s, %s, %s, %s)"
                values_to_insert = []
                for i, (content, embedding, source, page_number) in enumerate(
                    zip(contents, embeddings, sources, page_numbers)
                ):
                    values_to_insert.append(
                        (str(uuid.uuid4()), content, source, json.dumps(embedding), page_number)
                    )
                cursor.executemany(insert_query, values_to_insert)

            else:
                print(f"No files found in bucket {bucket_name}.")
            conn.commit()
    except Exception as e:
            conn.rollback()
            raise e
    finally:
        conn.close()
if __name__ == "__main__":
    main()