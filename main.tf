# https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service
# https://ruanmartinelli.com/posts/terraform-cloud-run


# https://fabianlee.org/2021/09/24/terraform-using-json-files-as-input-variables-and-local-variables/
locals {
  spreaker_access = jsondecode(file("${path.module}/auth/.spreaker/access.json"))
  google_access = jsondecode(file("${path.module}/auth/.google/access.json"))
}

provider "google" {
  project = "spoken-news"
  region = "us-west1"
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

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal"
    }
  }

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api]
}


resource "google_pubsub_topic" "news_topic" {
  name = "news-trigger-topic"
}

resource "google_pubsub_topic" "news_topic_dlq" {
  name = "news-trigger-topic-dlq"
}

resource "google_service_account" "pubsub_invoker" {
  account_id   = "cloud-run-pubsub-invoker"
  display_name = "Cloud Run Pub/Sub Invoker"
}

resource "google_cloud_run_service_iam_binding" "pubsub_to_run_invoker" {
  location = google_cloud_run_service.run_service.location
  service = google_cloud_run_service.run_service.name
  role = "roles/run.invoker"
  members = ["serviceAccount:${google_service_account.pubsub_invoker.email}"]
  depends_on = [ google_cloud_run_service.run_service
               , google_service_account.pubsub_invoker
               ]
}

resource "google_pubsub_subscription" "news_subscription" {
  name  = "news-trigger-topic-subscription"
  topic = google_pubsub_topic.news_topic.name

  push_config {
    push_endpoint = google_cloud_run_service.run_service.status[0].url
    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
    }
    attributes = {
      # Controls format
      x-goog-version = "v1"
    }
  }

  message_retention_duration = "600s"
  ack_deadline_seconds = 60
  retry_policy {
    minimum_backoff = "60s"
  }
  dead_letter_policy {
    dead_letter_topic = google_pubsub_topic.news_topic_dlq.id
    max_delivery_attempts = 5
  }
}


resource "google_cloud_scheduler_job" "scheduled-job" {
  name        = "news-job"
  description = "trigger the news process"

  # https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules
  # https://www.shellhacks.com/crontab-format-cron-job-examples-linux/
  # .---------------- minute (0 - 59)
  # | .-------------- hour (0 - 23)
  # | | .------------ day of month (1 - 31)
  # | | | .---------- month (1 - 12) OR jan,feb,mar ...
  # | | | | .-------- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue ...
  # | | | | |
  # * * * * *
  schedule = "45 15 22 12 *"
  time_zone = "America/Los_Angeles"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.news_topic.id
    attributes = {
      # will be recieved by the POST endpoint
      spreaker_url = "https://api.spreaker.com"
      spreaker_show_id = 5657024
      spreaker_token = local.spreaker_access.access_token
      tts_api_key = local.google_access.api_key
    }
  }
}
