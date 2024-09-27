output "table_name" {
    value = aws_dynamodb_table.connection_table.name
    description = "Table name"
}