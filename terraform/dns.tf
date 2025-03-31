# Reference existing DNS zone
data "google_dns_managed_zone" "default" {
  name = "sdfingfd-xyz-zone"
}

# Create DNS records
resource "google_dns_record_set" "a" {
  name         = "${var.domain_name}."
  managed_zone = data.google_dns_managed_zone.default.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.default.address]
}

resource "google_dns_record_set" "cname" {
  name         = "www.${var.domain_name}."
  managed_zone = data.google_dns_managed_zone.default.name
  type         = "CNAME"
  ttl          = 300

  rrdatas = ["${var.domain_name}."]
} 