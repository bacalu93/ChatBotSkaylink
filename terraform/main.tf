provider "aws" {
  region  = "eu-central-1"
}

terraform {
	backend "s3" {
		key    = "chatbot-statefile.tfstate"
	}
}

######### Lambda Functions
module "create_jira_ticket" {
    source = "./module_lambda"
	name = "${var.project_name}-create-jira-ticket-${var.account_id}"
	source_dir = "../lambda_functions/create_jira_ticket"
	region = var.region
	account_id = var.account_id
	project_name = var.project_name
	map_tag = var.map_tag
}

module "websocket_connect" {
    source = "./module_lambda"
	name = "${var.project_name}-websocket-connect-${var.account_id}"
	source_dir = "../lambda_functions/websocket_connect"
	region = var.region
	account_id = var.account_id
	project_name = var.project_name
	map_tag = var.map_tag
}

module "websocket_default" {
    source = "./module_lambda"
	name = "${var.project_name}-websocket-default-${var.account_id}"
	source_dir = "../lambda_functions/websocket_default"
	websocket_url = "${module.websocket_gateway.websocket_url}/${module.websocket_gateway.stage_name}"
	table_name = module.connection_id_table.table_name
	knowledge_base_bucket = module.aurora_db.kb_bucket_name
	region = var.region
	account_id = var.account_id
	project_name = var.project_name
	map_tag = var.map_tag
	jira_lambda = module.create_jira_ticket.lambda_name
}

module "websocket_disconnect" {
    source = "./module_lambda"
	name = "${var.project_name}-websocket-disconnect-${var.account_id}"
	source_dir = "../lambda_functions/websocket_disconnect"
	table_name = module.connection_id_table.table_name
	chat_history_bucket = module.chat_history_bucket.bucket_name
	region = var.region
	account_id = var.account_id
	project_name = var.project_name
	map_tag = var.map_tag
}


module "start_update_job" {
    source = "./module_lambda"
	name = "${var.project_name}-start-update-job-${var.account_id}"
	source_dir = "../lambda_functions/start_update_job"
	region = var.region
	account_id = var.account_id
	project_name = var.project_name
	map_tag = var.map_tag
	batch_job_definition = module.knowledge_base_update_batch_job.batch_job_arn
	batch_job_queue = module.knowledge_base_update_batch_job.batch_queue_arn
}



######### API Gateway
module "websocket_gateway" {
    source = "./module_api_gateway_websocket"
	name = "${var.project_name}-websocket-${var.account_id}"
	connect_lambda_arn = module.websocket_connect.lambda_arn
	connect_lambda_name = module.websocket_connect.lambda_name
	default_lambda_arn = module.websocket_default.lambda_arn
	default_lambda_name = module.websocket_default.lambda_name
	disconnect_lambda_arn = module.websocket_disconnect.lambda_arn
	disconnect_lambda_name = module.websocket_disconnect.lambda_name
	project_name = var.project_name
	map_tag = var.map_tag
}


######### Dynamo DB
module "connection_id_table" {
    source = "./module_dynamo_db"
	name = "${var.project_name}-dynamo-table-${var.account_id}"
	project_name = var.project_name
	map_tag = var.map_tag
}



######### Batch Job
module "knowledge_base_update_batch_job" {
    source = "./module_batch_job"
	name = "kb_update_batch_job"
	image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.project_name}-update-knowledge-base:${var.image_tag}"
	db_name = module.aurora_db.database_name
	db_host = module.aurora_db.host
	db_port = module.aurora_db.port 
	secret_arn = module.aurora_db.secret_arn 
	vpc_id = module.aurora_db.vpc_id
	region = var.region
	account_id = var.account_id
	cluster_arn = module.aurora_db.cluster_arn
	kb_name = "${var.project_name}-knowledge-base"
	kb_role_arn = module.aurora_db.kb_role_arn
	kb_bucket_arn = module.aurora_db.kb_bucket_arn
	kb_bucket_name = module.aurora_db.kb_bucket_name
	project_name = var.project_name
	map_tag = var.map_tag
}

######### Aurora for knowledge base
module "aurora_db" {
    source = "./module_aurora_knowledge_base"
	project_name = var.project_name
	username = "db_user"
	region = var.region
	account_id = var.account_id
	cidr_blocks = ["10.0.2.0/24", "10.0.3.0/24"]
	batch_security_group = module.knowledge_base_update_batch_job.batch_security_group_name
	map_tag = var.map_tag
}

######### Additional S3 buckets
module "chat_history_bucket" {
    source = "./module_s3_bucket"
	bucket_name = "${var.project_name}-chat-history-${var.account_id}"
	project_name = var.project_name
	map_tag = var.map_tag
}


######### Role for Amplify
module "amplify_role" {
    source = "./module_amplify_role"
	project_name = var.project_name
	region = var.region
	account_id = var.account_id
	map_tag = var.map_tag
}
