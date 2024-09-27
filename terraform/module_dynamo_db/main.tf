resource "aws_dynamodb_table" "connection_table" {
  name           = "${var.name}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "ConnectionID"
  point_in_time_recovery {
    enabled = true
  }
  deletion_protection_enabled = true
  attribute {
    name = "ConnectionID"
    type = "S"
  }
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}
