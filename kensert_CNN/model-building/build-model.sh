#!/bin/sh -e
### model building script

# test run docker build
cd /home
docker build --rm -t snapple49/pipelines-kensert-serving:test .
docker push snapple49/pipelines-kensert-serving:test
