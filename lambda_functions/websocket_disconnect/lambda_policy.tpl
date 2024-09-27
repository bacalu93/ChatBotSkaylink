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
            "Sid": "DynamoDelete",
            "Effect": "Allow",
            "Action": [
                "dynamodb:DeleteItem",
                "dynamodb:GetItem"
            ],
            "Resource": "arn:aws:dynamodb:${region}:${account_id}:table/${table_name}"
        },
        {
            "Action": [
                "s3:PutObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::${chat_history_bucket}/*",
            "Sid": "S3"
        }
    ],
    "Version": "2012-10-17"
}