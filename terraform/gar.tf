

resource "google_artifact_registry_repository" "services-repository" {
  project       = "solveit-369711"
  location      = "europe-west4"
  repository_id = "services-repository"
  description   = "Repository for service images"
  format        = "DOCKER"
  provider      = google-beta
}

