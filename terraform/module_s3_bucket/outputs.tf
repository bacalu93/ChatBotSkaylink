output "bucket_name" {
    value = aws_s3_bucket.mybucket.id
    description = "Bucket Name"
}