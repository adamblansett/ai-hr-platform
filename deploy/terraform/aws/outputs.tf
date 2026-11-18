output "aurora_endpoint" {
  description = "RDS Aurora PostgreSQL Cluster Primary Endpoint"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis Primary Host"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "s3_vault_bucket" {
  description = "Encrypted S3 Document Vault Bucket Name"
  value       = aws_s3_bucket.document_vault.bucket
}

output "kms_key_arn" {
  description = "KMS Encryption Key ARN"
  value       = aws_kms_key.hr_vault_key.arn
}
