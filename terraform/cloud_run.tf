# Backend Cloud Run Service
resource "google_cloud_run_v2_service" "backend" {
  name     = "weather-app-backend"
  location = var.region

  template {
    containers {
      image = var.backend_image
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Frontend Cloud Run Service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "weather-app-frontend"
  location = var.region

  template {
    containers {
      image = var.frontend_image

      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Allow backend service to be invoked by the frontend
resource "google_cloud_run_service_iam_member" "backend_invoker" {
  location = google_cloud_run_v2_service.backend.location
  service  = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "weather-app-run-sa"
  display_name = "Service Account for Weather App Cloud Run Services"
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "cloud_run_sa_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent"
  ])

  role    = each.key
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  project = var.project_id
} 