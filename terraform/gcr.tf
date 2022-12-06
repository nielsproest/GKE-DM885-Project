

resource "google_artifact_registry_repository" "services-repository" {
  project       = var.project_id
  location      = var.region
  repository_id = "services-repository"
  description   = "Repository for service images"
  format        = "DOCKER"
  provider      = google-beta
}

resource "google_container_registry" "registry" {
  project       = var.project_id
  location      = "EU"
}

resource "google_storage_bucket_iam_member" "admin" {
  bucket = google_container_registry.registry.id
  role = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_storage_bucket_iam_member" "legacyBucketOwner" {
  bucket = google_container_registry.registry.id
  role = "roles/storage.legacyBucketOwner"
  member = "serviceAccount:${google_service_account.github_actions.email}"
}