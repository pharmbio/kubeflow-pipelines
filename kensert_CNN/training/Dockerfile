FROM pharmbio/kensert-cnn-base:latest

WORKDIR /home

COPY train.sh .
RUN mkdir output

ENTRYPOINT ["bash", "/home/train.sh"]