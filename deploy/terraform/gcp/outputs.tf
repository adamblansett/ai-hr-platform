output "cloud_sql_connection_name" {
  description = "Cloud SQL Instance Connection Name"
  value       = google_sql_database_instance.postgres_instance.connection_name
}

output "cloud_sql_ip" {
  description = "Cloud SQL Public IP Address"
  value       = google_sql_database_instance.postgres_instance.public_ip_address
}

output "gke_cluster_name" {
  description = "GKE Autopilot Cluster Name"
  value       = google_container_cluster.gke_cluster.name
}

output "storage_vault_bucket" {
  description = "Cloud Storage Vault Bucket"
  value       = google_storage_bucket.document_vault.name
}
