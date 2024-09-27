output "database_name" {
    value = aws_rds_cluster.db_cluster_1.database_name
    description = ""
}

output "host" {
    value = aws_rds_cluster_instance.rds_writer_instance.endpoint
    description = ""
}

output "port" {
    value = aws_rds_cluster.db_cluster_1.port
    description = ""
}

output "secret_arn" {
    value = aws_rds_cluster.db_cluster_1.master_user_secret[0].secret_arn
    description = ""
}

output "vpc_id" {
    value = aws_vpc.vpc_aurora.id
    description = ""
}

output "cluster_arn" {
    value = aws_rds_cluster.db_cluster_1.arn
    description = ""
}

output "kb_role_arn" {
    value = aws_iam_role.kb_role.arn
    description = ""
}

output "kb_bucket_arn" {
    value = aws_s3_bucket.kb_bucket.arn
    description = ""
}

output "kb_bucket_name" {
    value = aws_s3_bucket.kb_bucket.id
    description = ""
}