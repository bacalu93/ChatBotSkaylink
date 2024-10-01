variable "region" { 
    type = string 
    default = ""
}

variable "project_name" {
    type = string
    default = ""
}

variable "account_id" {
    type = string
    default = ""
}

variable "username" {
  description = "Username for the master DB user"
  type        = string
}

variable "cidr_blocks" {
  description = "Username for the master DB user"
  type        = list
}

variable "batch_security_group" {
  description = "Security group of the batch job"
  type        = string
}

variable "map_tag" {
  type = string
}

