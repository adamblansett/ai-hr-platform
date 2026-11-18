terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. KMS Key for Envelope Encryption
resource "aws_kms_key" "hr_vault_key" {
  description             = "KMS Key for ai-hr-platform document vault and secrets"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# 2. VPC & Networking
resource "aws_vpc" "hr_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.hr_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-1"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.hr_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-private-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.hr_vpc.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${var.project_name}-private-2"
  }
}

# 3. Encrypted S3 Document Vault (I-9, W-4, Compensation)
resource "aws_s3_bucket" "document_vault" {
  bucket        = "${var.project_name}-vault-${var.environment}"
  force_destroy = false
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vault_encryption" {
  bucket = aws_s3_bucket.document_vault.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.hr_vault_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "vault_block_public" {
  bucket = aws_s3_bucket.document_vault.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 4. RDS Aurora PostgreSQL with pgvector Support
resource "aws_db_subnet_group" "db_subnets" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_rds_cluster_parameter_group" "aurora_pgvector_pg" {
  name   = "${var.project_name}-aurora-pg"
  family = "aurora-postgresql16"

  parameter {
    name  = "shared_preload_libraries"
    value = "vector"
  }
}

resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = "${var.project_name}-aurora"
  engine                  = "aurora-postgresql"
  engine_version          = "16.1"
  database_name           = "ai_hr_db"
  master_username         = "ai_hr_admin"
  master_password         = "ChangeMeInVaultProduction123!"
  db_subnet_group_name    = aws_db_subnet_group.db_subnets.name
  kms_key_id              = aws_kms_key.hr_vault_key.arn
  storage_encrypted       = true
  skip_final_snapshot     = true
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.aurora_pgvector_pg.name
}

resource "aws_rds_cluster_instance" "cluster_instances" {
  count              = 2
  identifier         = "${var.project_name}-node-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora_cluster.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.aurora_cluster.engine
  engine_version     = aws_rds_cluster.aurora_cluster.engine_version
}

# 5. ElastiCache Redis (Rate Limiting & Celery Task Broker)
resource "aws_elasticache_subnet_group" "redis_subnets" {
  name       = "${var.project_name}-redis-subnets"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnets.name
}
