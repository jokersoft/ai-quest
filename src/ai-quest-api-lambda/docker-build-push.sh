#!/usr/bin/env bash

set -e

image_tag="$1"

if [ -z "$image_tag" ]; then
  echo "Error: Image tag argument is missing."
  exit 1
fi

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $PROJECT_ID.dkr.ecr.eu-central-1.amazonaws.com
docker build -t api-lambda . --no-cache
docker tag api-lambda $PROJECT_ID.dkr.ecr.eu-central-1.amazonaws.com/ai-quest/api-lambda:"$image_tag"
docker push $PROJECT_ID.dkr.ecr.eu-central-1.amazonaws.com/ai-quest/api-lambda:"$image_tag"
