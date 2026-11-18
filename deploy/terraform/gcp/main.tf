terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# 1. VPC Network
resource "google_compute_network" "hr_vpc" {
  name                    = "ai-hr-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "hr_subnet" {
  name          = "ai-hr-subnet-${var.environment}"
  ip_cidr_range = "10.10.0.0/20"
  region        = var.gcp_region
  network       = google_compute_network.hr_vpc.id
}

# 2. Cloud Storage Vault (KMS Encrypted)
resource "google_storage_bucket" "document_vault" {
  name          = "ai-hr-vault-${var.gcp_project_id}-${var.environment}"
  location      = var.gcp_region
  force_destroy = false

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

# 3. Cloud SQL PostgreSQL 16 with pgvector
resource "google_sql_database_instance" "postgres_instance" {
  name             = "ai-hr-pg16-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.gcp_region

  settings {
    tier = var.db_tier

    database_flags {
      name  = "cloudsql.enable_pgvector"
      value = "on"
    }

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled = true
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "ai_hr_db" {
  name     = "ai_hr_db"
  instance = google_sql_database_instance.postgres_instance.name
}

# 4. GKE Autopilot Cluster
resource "google_container_cluster" "gke_cluster" {
  name     = "ai-hr-gke-${var.environment}"
  location = var.gcp_region

  enable_autopilot = true
  network          = google_compute_network.hr_vpc.name
  subnetwork       = google_compute_subnetwork.hr_subnet.name

  ip_allocation_policy {}
}
