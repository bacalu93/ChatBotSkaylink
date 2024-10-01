resource "null_resource" "pip_install" {
  triggers = {
    always_run = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = <<-EOT
      # List the contents of the layer directory to check for requirements.txt
      echo "Checking layer directory"
      ls -la ${var.source_dir}/layer/
      
      # Create a virtual environment and ensure pip is installed manually
      echo "Creating virtual environment"
      python3 -m venv venv --without-pip
      curl https://bootstrap.pypa.io/get-pip.py | ./venv/bin/python
      ./venv/bin/python -m ensurepip --upgrade
      ./venv/bin/python --version
      ./venv/bin/python -m pip --version
      ./venv/bin/python -m pip list
      
      # Install application dependencies using the virtual environment's Python
      if [ -s ${var.source_dir}/layer/requirements.txt ]; then
        echo "Installing requirements"
        ./venv/bin/python -m pip install --upgrade pip
        ./venv/bin/python -m pip install -r ${var.source_dir}/layer/requirements.txt --no-cache-dir -t ${var.source_dir}/layer/python/lib/python3.12/site-packages
      else
        echo "requirements.txt not found!"
      fi
      
      # Verify installation of dependencies
      ./venv/bin/python -m pip list | grep -E 'jose|requests'
      
      # Activate virtual environment before running tests
      source ./venv/bin/activate
      
      # Install pytest and boto3
      ./venv/bin/python -m pip install pytest boto3
      
      # Run tests if the tests folder exists
      if [ -d "${var.source_dir}/tests" ]; then
        echo "Running tests"
        ./venv/bin/python -m pytest ${var.source_dir}/tests
      else
        echo "Tests folder does not exist, skipping tests."
      fi
    EOT
  }
}






# for creating a lambda function the source file has to be in a zip folder
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${var.source_dir}/src"
  output_path = "${var.source_dir}/src.zip"
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${var.source_dir}/layer"
  output_path = "${var.source_dir}/layer.zip"
  depends_on  = [null_resource.pip_install]
  count       = "${fileexists("${var.source_dir}/layer/requirements.txt") && length(trimspace(file("${var.source_dir}/layer/requirements.txt"))) > 0 ? 1 : 0}"

}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = "${var.project_name}-layer"
  filename            = data.archive_file.layer[count.index].output_path
  source_code_hash    = data.archive_file.layer[count.index].output_base64sha256
  compatible_runtimes = ["python3.12"]
  count               = length(data.archive_file.layer)
}

# lambda function
resource "aws_lambda_function" "function" {
  function_name    = "${var.name}"
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.code.output_path
  source_code_hash = data.archive_file.code.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  layers           = length(aws_lambda_layer_version.layer) == 1 ? [aws_lambda_layer_version.layer[0].arn] : []
  timeout = 300
  depends_on       = [
    aws_iam_role_policy_attachment.lambda_policy_atch,
    aws_cloudwatch_log_group.log_group_lambda,
  ]
  environment {
    variables = { 
      WEBSOCKET_URL = replace("${var.websocket_url}", "wss://", "https://")
      TABLE_NAME = "${var.table_name}"
      CHAT_HISTORY_BUCKET = "${var.chat_history_bucket}"
      REGION = "${var.region}"
      PROJECT_NAME = "${var.project_name}"
      BATCH_JOB_DEFINITION = "${var.batch_job_definition}"
      BATCH_JOB_QUEUE = "${var.batch_job_queue}"
      JIRA_LAMBDA = "${var.jira_lambda}"
    }
  }
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

# create a cloudwatch log group
resource "aws_cloudwatch_log_group" "log_group_lambda" {
  name              = "/aws/lambda/${var.name}" 
  retention_in_days = 7
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.name}-policy"
  path        = "/"
  description = "IAM policy for logging from a lambda function, starting stepfunctions and access ssm parameters"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  policy = templatefile("${var.source_dir}/lambda_policy.tpl", {
    region                = "${var.region}",
    account_id            = "${var.account_id}",
    log_group_name        = aws_cloudwatch_log_group.log_group_lambda.name
    table_name            = "${var.table_name}"
    chat_history_bucket   = "${var.chat_history_bucket}"
    knowledge_base_bucket = "${var.knowledge_base_bucket}"
    batch_job_definition  = "${var.batch_job_definition}"
    batch_job_queue       = "${var.batch_job_queue}"
    jira_lambda           = "${var.jira_lambda}"
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_atch" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# create an IAM role for the lambda function
resource "aws_iam_role" "lambda_role" {
  name               = "${var.name}-role"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  }
  EOF
}