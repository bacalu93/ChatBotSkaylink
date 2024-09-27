import json
import boto3

def lambda_handler(event, context):
    print(event)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
