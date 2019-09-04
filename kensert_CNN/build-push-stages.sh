docker build -t pharmbio/pipelines-kensert-preprocess:test preprocess/
docker build -t pharmbio/pipelines-kensert-training:test training/
docker push pharmbio/pipelines-kensert-preprocess:test
docker push pharmbio/pipelines-kensert-training:test