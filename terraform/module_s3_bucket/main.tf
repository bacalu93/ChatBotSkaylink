resource "aws_s3_bucket" "mybucket" {
  bucket = var.bucket_name

  tags = {
    CreatedBy   = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.mybucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.mybucket.id
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
              "${aws_s3_bucket.mybucket.arn}",
              "${aws_s3_bucket.mybucket.arn}/*"
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
