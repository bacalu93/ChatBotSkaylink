resource "aws_iam_role" "main_role" {
  name = "${var.project_name}-role-amplify"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "amplify.amazonaws.com"
        }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "main_role_attachment" {
  role       = aws_iam_role.main_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess-Amplify"
}

resource "aws_iam_role_policy_attachment" "backend_role_attachment" {
  role       = aws_iam_role.main_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmplifyBackendDeployFullAccess"
}



resource "aws_iam_policy" "policy_amplify" {
  name        = "${var.project_name}-amplify-policy"
  description = "logging"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "PushLogs",
			"Effect": "Allow",
			"Action": [
				"logs:CreateLogStream",
				"logs:PutLogEvents"
			],
			"Resource": "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/amplify/*:log-stream:*"
		},
		{
			"Sid": "CreateLogGroup",
			"Effect": "Allow",
			"Action": "logs:CreateLogGroup",
			"Resource": "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/amplify/*"
		},
		{
			"Sid": "DescribeLogGroups",
			"Effect": "Allow",
			"Action": "logs:DescribeLogGroups",
			"Resource": "arn:aws:logs:${var.region}:${var.account_id}:log-group:*"
		}
	]
}
EOF
}

resource "aws_iam_role_policy_attachment" "logging_attachment" {
  role       = aws_iam_role.main_role.name
  policy_arn = aws_iam_policy.policy_amplify.arn
}