output "websocket_url" {
    value = aws_apigatewayv2_api.websocket_api.api_endpoint
    description = "Websocket URL"
}

output "stage_name" {
    value = aws_apigatewayv2_stage.prod.name
    description = "Stage name"
}