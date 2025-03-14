#! /bin/bash

set -x
outfile="$1"

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

save_logs() {
  podman-compose -f docker/docker-compose.yml logs --names > "$outfile"
  down
}

trap "save_logs" SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM

down
up || exit 1
save_logs
