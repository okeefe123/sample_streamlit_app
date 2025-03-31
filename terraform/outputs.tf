output "frontend_url" {
  value       = google_cloud_run_v2_service.frontend.uri
  description = "URL of the frontend Cloud Run service"
}

output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "URL of the backend Cloud Run service"
}

output "load_balancer_ip" {
  value       = google_compute_global_address.default.address
  description = "IP address of the load balancer"
}

output "nameservers" {
  value       = google_dns_managed_zone.default.name_servers
  description = "Nameservers for your domain"
} 