resource "aws_batch_job_definition" "batch_job_def" {
  name = "${var.project_name}_batch_job_def_${var.name}"
  type = "container"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  container_properties = <<CONTAINER_PROPERTIES
{
    "command": [],
    "image": "${var.image_name}",
    "privileged": false,
    "readonlyRootFilesystem": false,
    "resourceRequirements": [
    {"type": "VCPU", "value": "2"},
    {"type": "MEMORY", "value": "4000"}
  ],
    "environment": [
        {"name": "DB_NAME", "value": "${var.db_name}"},
        {"name": "DB_PORT", "value": "${var.db_port}"},
        {"name": "DB_HOST", "value": "${var.db_host}"},
        {"name": "SECRET_ARN", "value": "${var.secret_arn}"},
        {"name": "REGION", "value": "${var.region}"},
        {"name": "CLUSTER_ARN", "value": "${var.cluster_arn}"},
        {"name": "KB_NAME", "value": "${var.kb_name}"},
        {"name": "KB_ROLE_ARN", "value": "${var.kb_role_arn}"},
        {"name": "KB_BUCKET_ARN", "value": "${var.kb_bucket_arn}"},
        {"name": "KB_BUCKET_NAME", "value": "${var.kb_bucket_name}"}
    ]
}
CONTAINER_PROPERTIES
}