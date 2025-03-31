variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

variable "frontend_image" {
  description = "The full path to the frontend container image"
  type        = string
}

variable "backend_image" {
  description = "The full path to the backend container image"
  type        = string
}

variable "domain_name" {
  description = "The domain name for your application"
  type        = string
}

variable "admin_email" {
  description = "Your Google account email for IAP access"
  type        = string
} 