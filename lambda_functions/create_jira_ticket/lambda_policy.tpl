{
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:logs:${region}:${account_id}:log-group:${log_group_name}:*"
        },
        {
        "Action": [
            "ssm:GetParameter"
            ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:ssm:${region}:${account_id}:parameter/jira_api_token"    
        ]
        },
        {
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": "arn:aws:bedrock:${region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        }
    ],
    "Version": "2012-10-17"
}