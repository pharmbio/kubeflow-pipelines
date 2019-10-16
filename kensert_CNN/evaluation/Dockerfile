FROM pharmbio/kensert-cnn-base:latest

WORKDIR /home

COPY eval.sh .
COPY check_pass.py .
RUN mkdir output && mkdir /home/evaluation_results

ENTRYPOINT ["bash", "/home/eval.sh"]