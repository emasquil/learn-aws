#!/bin/bash

docker run \
--rm \
-d \
-v ml_models:/app/ml_models \
--name fastapi-pytorch \
-p 8000:80 \
fastapi-pytorch
