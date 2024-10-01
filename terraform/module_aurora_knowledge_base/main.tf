resource "aws_s3_bucket" "kb_bucket" {
  bucket        = "${var.project_name}-knowledge-${var.account_id}"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "kb_bucket_encryption" {
  bucket = aws_s3_bucket.kb_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_policy" "bucket_policy_kb" {
  bucket = aws_s3_bucket.kb_bucket.id
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Id": "SSLPolicy",
    "Statement": [
        {
            "Sid": "AllowSSLRequestsOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
              "${aws_s3_bucket.kb_bucket.arn}",
              "${aws_s3_bucket.kb_bucket.arn}/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
EOF
}

resource "aws_vpc" "vpc_aurora" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
    Name = "${var.project_name}_main_vpc"
  }
}

data "aws_availability_zones" "available" {
    state = "available"
}

resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.vpc_aurora.id
  cidr_block              = "${var.cidr_blocks[count.index]}"
  availability_zone       = "${data.aws_availability_zones.available.names[count.index]}"
  map_public_ip_on_launch = false
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
    Tier = "private"
  }
  depends_on = [ aws_vpc.vpc_aurora ]
}

## subnet-group
resource "aws_db_subnet_group" "subnetg-default" {
  name        = "${var.project_name}-rds-subnetg-${var.account_id}"
  subnet_ids = toset([for subnet in aws_subnet.private : subnet.id if subnet.vpc_id == aws_vpc.vpc_aurora.id && subnet.tags["Tier"] == "private"])
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
    Name = "${var.project_name}-rds-subnetg-${var.account_id}"
  }
  depends_on = [ aws_subnet.private ]
}

## parameter-group
resource "aws_rds_cluster_parameter_group" "pgroup-default" {
  name   = "${var.project_name}-rds-pgroup-${var.account_id}"
  family = "aurora-postgresql15"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  parameter {
    name  = "log_connections"
    value = "1"
  }
}

## security-group
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.vpc_aurora.id

  ingress = []
  egress  = []
  
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }

}

resource "aws_security_group" "sg-default" {
  name   = "${var.project_name}-rds-sg-${var.account_id}"
  vpc_id = aws_vpc.vpc_aurora.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [var.batch_security_group]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
    Name = "${var.project_name}-rds-sg-${var.account_id}"
  }
}

## Password 
resource "random_password" "db_master_pwd" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# RDS logs
resource "aws_cloudwatch_log_group" "rds_logs" {
  name              = "/aws/rds/cluster/cluster-${var.project_name}-${var.account_id}/postgresql"
  retention_in_days = 7
}


## Cluster PostgreSql
resource "aws_rds_cluster" "db_cluster_1" {
  cluster_identifier = "${var.project_name}-cluster-${var.account_id}"
  engine             = "aurora-postgresql"
  engine_version     = "15.4"
  engine_mode        = "provisioned"

  database_name      = "dbgenaichatbot${var.account_id}"
  storage_encrypted  = true
  skip_final_snapshot    = true
  enable_http_endpoint = true
  backup_retention_period = 7
  iam_database_authentication_enabled = true
  enabled_cloudwatch_logs_exports = toset(["postgresql"])
  deletion_protection = true
  copy_tags_to_snapshot = true

  master_username    = var.username
  manage_master_user_password = true

  vpc_security_group_ids = [aws_security_group.sg-default.id]
  db_subnet_group_name   = aws_db_subnet_group.subnetg-default.name
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.pgroup-default.name

  serverlessv2_scaling_configuration {
    max_capacity = 4.0
    min_capacity = 0.5
  }

  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }

  depends_on = [
    aws_security_group.sg-default,
    aws_db_subnet_group.subnetg-default,
    aws_rds_cluster_parameter_group.pgroup-default,
    aws_cloudwatch_log_group.rds_logs
  ]
}

resource "aws_rds_cluster_instance" "rds_writer_instance" {
  cluster_identifier = aws_rds_cluster.db_cluster_1.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.db_cluster_1.engine
  engine_version     = aws_rds_cluster.db_cluster_1.engine_version
  monitoring_interval = 30
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_iam_role" "kb_role" {
  name = "${var.project_name}-AmazonBedrockExecutionRoleForKnowledgeBase_kb-role"
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
            "Sid": "AmazonBedrockKnowledgeBaseTrustPolicy",
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "${var.account_id}"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:bedrock:${var.region}:${var.account_id}:knowledge-base/*"
                }
            }
        }
    ]
}
EOF
}

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name        = "${var.project_name}-rds-enhanced-monitoring-role"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RDSEnhancedMonitoringTrustPolicy",
            "Effect": "Allow",
            "Principal": {
                "Service": "monitoring.rds.amazonaws.com"
            },
            "Action": "sts:AssumeRole"          
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}



resource "aws_iam_policy" "kb_policy" {
  name        = "${var.project_name}-kb-policy"
  description = "Policy for knowledge base"
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
        "${aws_rds_cluster.db_cluster_1.master_user_secret[0].secret_arn}"
      ]
    },
    {
      "Action": [
        "rds-data:ExecuteStatement",
        "rds-data:BatchExecuteStatement",
        "rds:DescribeDBClusters"
        ],
      "Effect": "Allow",
      "Resource": [
         "${aws_rds_cluster.db_cluster_1.arn}"
      ]
    },
    {
      "Action": [
        "bedrock:CreateDataSource"
        ],
      "Effect": "Allow",
      "Resource": [
         "${aws_s3_bucket.kb_bucket.arn}",
         "${aws_s3_bucket.kb_bucket.arn}/*"
      ]
    },
    {
        "Action": [
            "bedrock:InvokeModel"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:bedrock:eu-central-1::foundation-model/cohere.embed-multilingual-v3"
        ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "kb_attachement" {
  role       = aws_iam_role.kb_role.name
  policy_arn = aws_iam_policy.kb_policy.arn
}


### ec2 flow log
resource "aws_flow_log" "flowlogs" {
  iam_role_arn    = aws_iam_role.flowlogrole.arn
  log_destination = aws_cloudwatch_log_group.flowloggroup.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.vpc_aurora.id
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_cloudwatch_log_group" "flowloggroup" {
  name              = "vpc/${var.project_name}/flowlogs"
  retention_in_days = 7

}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "flowlogrole" {
  name               =  "${var.project_name}-flowlog-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "flowlogpolicydoc" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "flowlogpolicy" {
  name   = "${var.project_name}-flowlog-policy"
  role   = aws_iam_role.flowlogrole.id
  policy = data.aws_iam_policy_document.flowlogpolicydoc.json
}