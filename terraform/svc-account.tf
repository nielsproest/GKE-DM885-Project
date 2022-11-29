/*resource "google_service_account" "github_actions_service_account" {
  account_id   = "github-actions-id"
  display_name = "Github Action Service Account"
}

resource "google_project_iam_member" "github_actions_roles" {
  project = local.project_id
  role    = "roles/iam.workloadIdentityPoolAdmin"
  member  = "serviceAccount:${google_service_account.github-actions-id.email}"
}


resource "google_service_account_key" "github_actions_service_account_key" {
  service_account_id = google_service_account.myaccount.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}*/




locals {
  project_id = "solveit-369711"
  repo       = "TroelsLind/DM885-Project"
}

resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = local.project_id
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub pool"
  description               = "Identity pool for GitHub deployments"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = local.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.aud"        = "assertion.aud"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}




resource "google_service_account" "github_actions" {
  project      = local.project_id
  account_id   = "github-actions"
  display_name = "Service Account used for GitHub Actions"
}

resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${local.repo}"
}


output "workload_identity_provider" {
  value = "${google_iam_workload_identity_pool.github_pool.name}/providers/${google_iam_workload_identity_pool_provider.github.workload_identity_pool_provider_id}"
}

output "service_account" {
  value = google_service_account.github_actions.email
}



resource "google_project_iam_binding" "github_actions_kubernetes_dev" {
  role = "roles/container.developer"
  project = local.project_id
  members  = ["serviceAccount:${google_service_account.github_actions.email}"]
}


resource "google_project_iam_binding" "github_actions_artifact_writer" {
  role = "roles/artifactregistry.admin"
  project = local.project_id
  members  = ["serviceAccount:${google_service_account.github_actions.email}"]
}

data "google_iam_policy" "admin" {
  binding {
    role = "roles/artifactregistry.admin"
    members = ["serviceAccount:${google_service_account.github_actions.email}"]
  }
}

resource "google_artifact_registry_repository_iam_policy" "policy" {
  project = local.project_id
  location = google_artifact_registry_repository.services-repository.location
  repository = google_artifact_registry_repository.services-repository.name
  policy_data = data.google_iam_policy.admin.policy_data
}


/*
resource "google_artifact_registry_repository_iam_binding" "github-actions-repo-iam" {
  provider = google-beta
  project = local.project_id

  location = google_artifact_registry_repository.services-repository.location
  repository = google_artifact_registry_repository.services-repository.name

  role = "roles/artifactregistry.admin"
  members  = ["serviceAccount:${google_service_account.github_actions.email}"]
}
*/