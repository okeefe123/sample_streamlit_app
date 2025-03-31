# Reserve an external IP address
resource "google_compute_global_address" "default" {
  name = "weather-app-ip"
}

# Create HTTPS certificate
resource "google_compute_managed_ssl_certificate" "default" {
  name = "weather-app-cert"

  managed {
    domains = [var.domain_name]
  }
}

# Create a backend service for the Cloud Run frontend
resource "google_compute_backend_service" "default" {
  name                  = "weather-app-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"

  iap {
    oauth2_client_id     = google_iap_client.default.client_id
    oauth2_client_secret = google_iap_client.default.secret
  }

  backend {
    group = google_compute_region_network_endpoint_group.cloudrun_neg.id
  }
}

# Create a Network Endpoint Group for the frontend Cloud Run service
resource "google_compute_region_network_endpoint_group" "cloudrun_neg" {
  name                  = "weather-app-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_v2_service.frontend.name
  }
}

# Create a URL map
resource "google_compute_url_map" "default" {
  name            = "weather-app-url-map"
  default_service = google_compute_backend_service.default.id
}

# Create an HTTPS target proxy
resource "google_compute_target_https_proxy" "default" {
  name             = "weather-app-https-proxy"
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

# Create a forwarding rule
resource "google_compute_global_forwarding_rule" "default" {
  name                  = "weather-app-forwarding-rule"
  ip_address            = google_compute_global_address.default.id
  port_range            = "443"
  target                = google_compute_target_https_proxy.default.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# HTTP to HTTPS redirect
resource "google_compute_url_map" "http_redirect" {
  name = "weather-app-http-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "http_redirect" {
  name    = "weather-app-http-redirect-proxy"
  url_map = google_compute_url_map.http_redirect.id
}

resource "google_compute_global_forwarding_rule" "http_redirect" {
  name                  = "weather-app-http-redirect-rule"
  ip_address            = google_compute_global_address.default.id
  port_range            = "80"
  target                = google_compute_target_http_proxy.http_redirect.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# IAP OAuth client
resource "google_iap_client" "default" {
  display_name = "Weather App IAP"
  brand        = google_iap_brand.default.name
}

resource "google_iap_brand" "default" {
  support_email     = var.admin_email
  application_title = "Weather App"
}

# IAP access for your account
resource "google_iap_web_backend_service_iam_member" "member" {
  project             = var.project_id
  web_backend_service = google_compute_backend_service.default.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = "user:${var.admin_email}"
} 