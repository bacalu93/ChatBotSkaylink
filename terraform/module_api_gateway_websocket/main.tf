resource "aws_apigatewayv2_api" "websocket_api" {
  name                       = var.name
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
}

resource "aws_apigatewayv2_integration" "connect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.connect_lambda_arn
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_apigatewayv2_route" "connect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect_integration.id}"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_lambda_permission" "connect_lambda_permissions" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.connect_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "default_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.default_lambda_arn
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.default_integration.id}"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_apigatewayv2_route_response" "default_route_response" {
  api_id             = aws_apigatewayv2_api.websocket_api.id
  route_id           = aws_apigatewayv2_route.default_route.id
  route_response_key = "$default"
}

resource "aws_lambda_permission" "default_lambda_permissions" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.default_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "disconnect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.disconnect_lambda_arn
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_apigatewayv2_route" "disconnect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect_integration.id}"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_lambda_permission" "disconnect_lambda_permissions" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.disconnect_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "api_gw_access_logs" {
  name              = "api_gateway/${var.name}"
  retention_in_days = 7
}


resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.websocket_api.id
  name        = "${var.project_name}-prod"
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw_access_logs.arn
    format          = jsonencode(
          {
            caller            = "$context.identity.caller"
            extendedRequestId = "$context.extendedRequestId"
            httpMethod        = "$context.httpMethod"
            ip                = "$context.identity.sourceIp"
            protocol          = "$context.protocol"
            requestId         = "$context.requestId"
            requestTime       = "$context.requestTime"
            resourcePath      = "$context.resourcePath"
            responseLength    = "$context.responseLength"
            status            = "$context.status"
            user              = "$context.identity.user"
          }
      )
  }
  default_route_settings {
    data_trace_enabled = true
    logging_level = "INFO"
    throttling_rate_limit = 10000
    throttling_burst_limit = 5000
  }
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  depends_on    = [aws_api_gateway_account.gateway_account]
}

resource "aws_cloudwatch_log_group" "api_gw_execution_logs" {
  name              = "/aws/apigateway/${aws_apigatewayv2_api.websocket_api.id}/${aws_apigatewayv2_stage.prod.name}"
  retention_in_days = 7
}


resource "aws_iam_role" "apigateway_role" {
  name = "${var.name}-api-gateway-role"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "apigateway.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

resource "aws_iam_policy" "api_gateway_policy" {
  name        = "${var.name}-api-gateway-policy"
  path        = "/"
  description = "api_gateway_policy"
  tags = {
    CreatedBy = "Terraform"
    ProjectName = var.project_name
    map-migrated = var.map_tag
  }
  policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents",
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "lambda:InvokeFunction"
     ],
     "Resource": "*",
     "Effect": "Allow"
   }
 ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role       = aws_iam_role.apigateway_role.name
  policy_arn = aws_iam_policy.api_gateway_policy.arn
}


resource "aws_api_gateway_account" "gateway_account" {
  cloudwatch_role_arn = aws_iam_role.apigateway_role.arn
}