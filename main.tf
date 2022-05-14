# https://ruanmartinelli.com/posts/terraform-cloud-run
# https://github.com/RitreshGirdhar/google-cloud-run-with-scheduler-terraform
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started

#TODO pub/sub triggering, custom image
provider "google" {
  project = "spoken-news"
}

# Enables the Cloud Run API
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  name = "app"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/google-samples/hello-app:1.0"
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

