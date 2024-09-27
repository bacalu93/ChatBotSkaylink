import requests
from requests.auth import HTTPBasicAuth
import json
import boto3

ssm = boto3.client('ssm')

def summarize_conversation(conversation_history):
    # Initialize the Bedrock runtime client
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')

    # Craft the prompt to guide the LLM to summarize the conversation history
    prompt = f"""Human: You are an AI assistant specialized in creating Jira tickets. Analyze the following conversation history and create a Jira ticket summary and description. 

Conversation history:
{conversation_history}

Requirements:
1. Summary: Create a concise, title-like summary of the main issue (max 100 characters).
2. Description: Provide a detailed description of the problem, including key points and any relevant context (200-500 characters).

Please format your response as follows:
<summary>
[Concise, title-like summary here]
</summary>
<description>
[Detailed problem description here]
</description>"""

    kwargs = {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    }

    response = bedrock_runtime.invoke_model(**kwargs)
    body = json.loads(response['body'].read())
    
    response_text = body['content'][0]['text']

    # Extract the summary and important points from the response
    summary = extract_between_tags(response_text, "<summary>", "</summary>")
    description = extract_between_tags(response_text, "<description>", "</description>")

    return summary, description

def extract_between_tags(text, start_tag, end_tag):
    """
    Helper function to extract text between specific tags.
    """
    try:
        start = text.index(start_tag) + len(start_tag)
        end = text.index(end_tag, start)
        return text[start:end].strip()
    except ValueError:
        return "No data found"

def summarize_and_prepare_payload(conversation_history, user_mail):
    # Summarize the conversation and extract important points
    summary, description = summarize_conversation(conversation_history)

    # Prepare the payload using the summarized data
    payload = {
        "fields": {
            "summary": summary if summary else "Auto generated title",
            "description": f"{description}\n\nUser Mail: {user_mail}",
            "issuetype": {
                "name": "Feedback"  # Can be modified based on your specific issue type
            },
            "labels": [
                "Ge"
            ],
            "project": {
                "key": "GSC"
            },
            "priority": {
                "name": "Medium"
            }
        }
    }

    return json.dumps(payload)

def create_attachment(ticket_id, conversation_history, auth):
    url = f"https://actico.atlassian.net/rest/api/2/issue/{ticket_id}/attachments"

    chat_history_file = open('/tmp/chat_history.txt','w')
    chat_history_file.write(conversation_history)
    chat_history_file.close()

    headers = {
        'X-Atlassian-Token': 'no-check'
    }

    # Make the POST request to create the Jira ticket
    response = requests.request(
        "POST",
        url,
        headers=headers,
        auth=auth,
        files = {
             "file": ("chat_history.txt", open("/tmp/chat_history.txt","rb"), "text/plain")
        }
    ) 
    return response
    
def lambda_handler(event, context):
    print(event)
    try:
        # Extract the conversation history from the event
        conversation_history = event.get('conversation_history', 'No conversation history provided')
        conversation_history_string = ""
        for message in conversation_history:
            conversation_history_string += f"{message['role']}: {message['content'][0]['text']}\n"


        #ticket_content = event.get('ticket_content', 'No content')
        user_mail = event.get('user_mail', 'Unknown User')

        # Generate the Jira ticket payload using the summarized conversation
        payload = summarize_and_prepare_payload(conversation_history_string, user_mail)

        # Jira API details
        url = "https://actico.atlassian.net/rest/api/2/issue"
        api_token = ssm.get_parameter(Name='jira_api_token')['Parameter']['Value']
        auth = HTTPBasicAuth("michael.fischbacher@skaylink.com", api_token)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Make the POST request to create the Jira ticket
        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )
        if response.status_code == 201:
            ticket_id = json.loads(response.text)['id']
            response_attachment = create_attachment(ticket_id, conversation_history_string, auth)

            return {
                'statusCode': 200,
                'body': f'Ticket created successfully with id {ticket_id}'
            }


        else:
            return {
                'statusCode': response.status_code,
                'body': f"Failed to create ticket: {response.text}"
            }

    except Exception as e:
        print(f"Error during ticket creation: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Internal server error: {str(e)}"
        }

