{
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:logs:${region}:${account_id}:log-group:${log_group_name}"
        },
        {
            "Action": [
                "batch:SubmitJob"
            ],
            "Effect": "Allow",
            "Resource":[
                "${batch_job_definition}",
                "${batch_job_queue}"
            ]
        }
    ],
    "Version": "2012-10-17"
}