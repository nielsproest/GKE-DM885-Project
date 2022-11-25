

resource "google_artifact_registry_repository" "devops_repo" {
  location      = "europe-west4"
  repository_id = "services_repository"
  description   = "Repository for service images"
  format        = "DOCKER"
  provider      = google-beta
}

