#!/bin/sh -e
### model building script

cd /home
docker build --rm -t ${MODEL_REPO}/pipelines-kensert-serving:test .
docker push ${MODEL_REPO}/pipelines-kensert-serving:test
