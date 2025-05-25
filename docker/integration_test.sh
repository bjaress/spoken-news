#! /bin/bash

set -x
container_tool="$1"
shift
outfile="$1"

up() {
  "${container_tool}"-compose -f docker/docker-compose.yml up \
    --build \
    --remove-orphans \
    --exit-code-from app-tests \
    --abort-on-container-exit
}

down() {
  "${container_tool}"-compose -f docker/docker-compose.yml down --remove-orphans
}

save_logs() {
  "${container_tool}"-compose -f docker/docker-compose.yml logs --names > "$outfile"
  down
}

trap "save_logs" SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM

down
up || exit 1
save_logs
