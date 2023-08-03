#!/usr/bin/env bash

pip3 install -r requirements.txt -t build/
cp index.py build
cd build
zip -r artifact.zip .
