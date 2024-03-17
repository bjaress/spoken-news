#! /bin/bash

up() {
  podman-compose -f docker/docker-compose.yml up \
    --build \
    --remove-orphans \
    --exit-code-from app-tests \
    --abort-on-container-exit
}

down() {
  podman-compose -f docker/docker-compose.yml down --remove-orphans
}

trap "down" SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM

down
up
down
