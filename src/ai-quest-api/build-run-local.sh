#!/usr/bin/env bash

set -e
export DOCKER_BUILDKIT=1

docker build --platform linux/amd64 . -t ai-quest-api -f local.Dockerfile
docker run -p 8000:8000 \
  -v $(pwd)/app:/app \
  --env-file .env \
  ai-quest-api
