variable "name" {
  type = string
}

variable "source_dir" {
  type = string
}

variable "websocket_url" {
  type = string
  default = ""
}

variable "table_name" {
  type = string
  default = ""
}

variable "chat_history_bucket" {
  type = string
  default = ""
}

variable "knowledge_base_bucket" {
  type = string
  default = ""
}

variable "jira_lambda" {
  type = string
  default = ""
}

variable "project_name" {
  type = string
  default = ""
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "map_tag" {
  type = string
}

variable "batch_job_definition" {
  type = string
  default = ""
}

variable "batch_job_queue" {
  type = string
  default = ""
}