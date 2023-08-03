#!/usr/bin/env bash

set -e

docker build -t api-lambda --no-cache -f local.Dockerfile .
docker run -d -p 8000:8000 api-lambda
