resource "aws_batch_job_queue" "batch_queue" {
  name     = "${var.project_name}-job-queue-${var.name}"
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.batch_env_batch_job.arn
  }
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}
