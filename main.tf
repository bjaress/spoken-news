# https://ruanmartinelli.com/posts/terraform-cloud-run
# https://github.com/RitreshGirdhar/google-cloud-run-with-scheduler-terraform
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started

#TODO pub/sub triggering, custom image
provider "google" {
  project = "spoken-news"
}

# Might be a chicken-and-egg problem here
#resource "google_artifact_registry_repository" "app-repo" {
#  location = "us-central1"
#  repository_id = "app-repo"
#  description = "example docker repository"
#  format = "DOCKER"
#}

# Enables the Cloud Run API
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}


variable "docker_image" {
  type = string
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  name = "app"
  location = "us-central1"

  template {
    spec {
      containers {
        image = var.docker_image
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api]
}

#### TODO replace with scheduled pub/sub
## Allow unauthenticated users to invoke the service
#resource "google_cloud_run_service_iam_member" "run_all_users" {
#  service  = google_cloud_run_service.run_service.name
#  location = google_cloud_run_service.run_service.location
#  role     = "roles/run.invoker"
#  member   = "allUsers"
#}
## Display the service URL
#output "service_url" {
#  value = google_cloud_run_service.run_service.status[0].url
#}
