resource "aws_iam_role" "ecs_instance_role" {
  name = "${var.project_name}_ecs_instance_role_${var.name}"
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
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
          "Service": "ec2.amazonaws.com"
        }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_attachment" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_policy" "policy_batch" {
  name        = "${var.project_name}_batchjob_policy"
  description = "CW and S3"
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "cloudwatch:PutMetricData",
        "secretsmanager:GetSecretValue"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:logs:*:*:*",
        "arn:aws:cloudwatch:*:*:metric/*",
        "${var.secret_arn}"
      ]
    },
    {
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::${var.kb_bucket_name}",
        "arn:aws:s3:::${var.kb_bucket_name}/*"
      ]
    },
    {
      "Action": [
        "bedrock:CreateKnowledgeBase",
        "bedrock:CreateDataSource",
        "bedrock:StartIngestionJob",
        "bedrock:GetKnowledgeBase",
        "bedrock:UpdateKnowledgeBase",
        "bedrock:UpdateDataSource"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:bedrock:${var.region}:${var.account_id}:knowledge-base/*"
      ]
    },
    {
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:bedrock:${var.region}::foundation-model/cohere.embed-multilingual-v3"
      ]
    },
    {
      "Action": [
        "iam:PassRole"
      ],
      "Effect": "Allow",
      "Resource": [
        "${var.kb_role_arn}"
      ]
    },
    {
      "Action": [
        "ssm:GetParameter",
        "ssm:PutParameter"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:ssm:${var.region}:${var.account_id}:parameter/datasource_id",
        "arn:aws:ssm:${var.region}:${var.account_id}:parameter/knowledgebase_id"    
      ]
    }    
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cw_logs" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = aws_iam_policy.policy_batch.arn
}

resource "aws_iam_instance_profile" "ecs_instance_role_profile" {
  name = "ecs_instance_role_${var.project_name}_${var.name}"
  role = aws_iam_role.ecs_instance_role.name
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_iam_role" "aws_batch_service_role" {
  name = "${var.project_name}_batch_service_role_${var.name}"
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
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
          "Service": "batch.amazonaws.com"
        }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_internet_gateway" "gw" {
  vpc_id = var.vpc_id
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_route_table" "batch_job_route_table" {
  vpc_id = var.vpc_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_route_table_association" "batch_job_route_table_association" {
  subnet_id      = aws_subnet.subnet_batch_job.id
  route_table_id = aws_route_table.batch_job_route_table.id
}

resource "aws_route_table_association" "batch_job_route_table_association2" {
  subnet_id      = aws_subnet.subnet_batch_job2.id
  route_table_id = aws_route_table.batch_job_route_table.id
}

resource "aws_security_group" "aws_security_group_batch_job" {
  name   = "${var.project_name}_batch_compute_env_sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.trusted_ip_range]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "subnet_batch_job" {
  vpc_id                = var.vpc_id
  cidr_block            = "10.0.0.0/24"
  map_public_ip_on_launch = true
  availability_zone = "${data.aws_availability_zones.available.names[0]}"
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_subnet" "subnet_batch_job2" {
  vpc_id                = var.vpc_id
  cidr_block            = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone = "${data.aws_availability_zones.available.names[1]}"
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_batch_compute_environment" "batch_env_batch_job" {
  compute_environment_name_prefix = "${var.project_name}_batch_env_${var.name}"

  lifecycle {
    create_before_destroy = true
  }

  compute_resources {
    instance_role         = aws_iam_instance_profile.ecs_instance_role_profile.arn
    instance_type         = ["optimal"]
    max_vcpus             = 16
    min_vcpus             = 0
    security_group_ids    = [aws_security_group.aws_security_group_batch_job.id]
    subnets               = [aws_subnet.subnet_batch_job.id, aws_subnet.subnet_batch_job2.id]
    type                  = "EC2"
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.aws_batch_service_role]
  tags = {
    CreatedBy    = "Terraform"
    ProjectName  = var.project_name
    map-migrated = var.map_tag
  }
}
