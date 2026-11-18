variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "ai-hr-platform-prod"
}

variable "gcp_region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "db_tier" {
  description = "Cloud SQL PostgreSQL machine tier"
  type        = string
  default     = "db-custom-4-16384"
}
