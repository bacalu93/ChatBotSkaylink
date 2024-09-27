import requests
from jose import jwt
import boto3
import os


def get_userpool_id():
    cognito_client = boto3.client('cognito-idp')
    response = cognito_client.list_user_pools(
        MaxResults = 60
    )
    
    for userpool in response['UserPools']:
        userpool_definition = cognito_client.describe_user_pool(
            UserPoolId=userpool['Id']
        )
        if userpool_definition['UserPool'].get('UserPoolTags',{}).get('ProjectName','') == os.getenv('PROJECT_NAME'):
            return userpool['Id']


def verify_token(event_content):  

    url = f"https://cognito-idp.{os.getenv('REGION')}.amazonaws.com/{get_userpool_id()}/.well-known/jwks.json"
        
    response = requests.get(url)
    keys = response.json()["keys"]
    accepted_tokens = [k["kid"] for k in keys]
    
    token = event_content['body']
    header = jwt.get_unverified_header(token)    
    
    if header['kid'] in accepted_tokens:
        return True
    else:
        return False