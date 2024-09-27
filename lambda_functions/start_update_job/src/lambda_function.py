import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    print(event)
    now = datetime.now()
    now_string = now.strftime('%Y-%m-%d-%H-%M-%S')

    client = boto3.client('batch')
    response = client.submit_job(
        jobName=f'update-knowlegdebase-{now_string}',
        jobQueue=os.getenv('BATCH_JOB_QUEUE'),
        jobDefinition=os.getenv('BATCH_JOB_DEFINITION'))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
