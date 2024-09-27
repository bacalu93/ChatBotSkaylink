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
            "Sid": "BedrockInvoke",
			"Effect": "Allow",
            "Action": [
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:Retrieve"
            ],
			"Resource": "*"
        },
        {
			"Sid": "DynamoGetPut",
			"Effect": "Allow",
			"Action": [
				"dynamodb:PutItem",
				"dynamodb:GetItem"
			],
			"Resource": "arn:aws:dynamodb:${region}:${account_id}:table/${table_name}"
		},
        {
            "Effect": "Allow",
            "Action": [
                "execute-api:Invoke",
                "execute-api:ManageConnections"
            ],
            "Resource": "arn:aws:execute-api:*:*:*"
        },
        {
        "Action": [
            "ssm:GetParameter"
            ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:ssm:${region}:${account_id}:parameter/knowledgebase_id"    
        ]
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::${knowledge_base_bucket}/*"
            ]
        },
        {
            "Action": [
                "cognito-idp:ListUserPools",
                "cognito-idp:DescribeUserPool"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "amplify:GetApp"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:lambda:${region}:${account_id}:function:${jira_lambda}"
        }
    ],
    "Version": "2012-10-17"
  }