output "lambda_arn" {
    value = aws_lambda_function.function.invoke_arn
    description = "Lambda Arn"
}

output "lambda_name" {
    value = aws_lambda_function.function.function_name
    description = "Lambda Name"
}