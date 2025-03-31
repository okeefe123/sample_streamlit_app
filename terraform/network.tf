# VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "weather-app-vpc"
  auto_create_subnetworks = false
}

# Subnet for Cloud Run
resource "google_compute_subnetwork" "subnet" {
  name          = "weather-app-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Serverless VPC Access connector
resource "google_vpc_access_connector" "connector" {
  name          = "weather-app-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.vpc_network.id
  region        = var.region
}

# Cloud NAT for outbound connectivity
resource "google_compute_router" "router" {
  name    = "weather-app-router"
  region  = var.region
  network = google_compute_network.vpc_network.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "weather-app-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
} 