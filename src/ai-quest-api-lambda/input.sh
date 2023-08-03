#!/bin/bash

payload=$@
url="http://localhost:8000/api/v1/action/"
curl -X POST "${url}" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"input\":\"${payload}\"}"
