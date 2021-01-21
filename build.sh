#!/usr/bin/env bash

poetry export -f requirements.txt > requirements.txt

docker build -t fastapi-pytorch .

rm requirements.txt
