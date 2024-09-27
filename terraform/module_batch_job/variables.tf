variable "name" {
  type = string
}

variable "image_name" {
  type = string
}

variable "trusted_ip_range" {
  description = "The trusted IP range for SSH access"
  type        = string
  default     = "192.168.0.0/16"  # Default trusted IP range; adjust as necessary
}

variable "db_name" {
  type = string
}

variable "db_port" {
  type = string
}

variable "db_host" {
  type = string
}

variable "secret_arn" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "cluster_arn" {
  type = string
}

variable "kb_name" {
  type = string
}

variable "kb_role_arn" {
  type = string
}

variable "kb_bucket_arn" {
  type = string
}

variable "kb_bucket_name" {
  type = string
}

variable "project_name" {
  type = string
}

variable "map_tag" {
  type = string
}