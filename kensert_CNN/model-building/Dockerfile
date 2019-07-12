#FROM pharmbio/kaniko-executor:latest
FROM docker:stable

WORKDIR /home

ADD ofaas_builder .
ADD build-model.sh .

ENTRYPOINT ["sh", "/home/build-model.sh"]