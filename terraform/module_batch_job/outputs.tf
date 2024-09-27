output "batch_job_arn" {
    value = aws_batch_job_definition.batch_job_def.arn
    description = "Batch Job Arn"
}

output "batch_queue_arn" {
    value = aws_batch_job_queue.batch_queue.arn
    description = "Batch Queue Arn"
}

output "batch_security_group_name" {
    value = aws_security_group.aws_security_group_batch_job.id
    description = "Batch security group name"
}
