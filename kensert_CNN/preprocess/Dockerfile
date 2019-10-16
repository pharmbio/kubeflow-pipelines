FROM pharmbio/kensert-cnn-base:latest

WORKDIR /home

COPY preprocess.sh .
RUN mkdir output

ENTRYPOINT ["bash", "/home/preprocess.sh"]