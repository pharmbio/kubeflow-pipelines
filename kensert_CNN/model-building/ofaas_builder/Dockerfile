FROM tensorflow/tensorflow:1.12.3-py3

WORKDIR /home

ADD https://github.com/openfaas/faas/releases/download/0.9.14/fwatchdog /usr/bin
ADD requirements.txt .

RUN chmod +x /usr/bin/fwatchdog && \
    apt update && apt install -y libsm6 libxext6 libxrender-dev && \
    pip3 install -r requirements.txt

ADD index.py .
ADD function ./function
ADD models/*.h5 ./function/predict_api/

ENV fprocess="python3 index.py"
ENV read_timeout=120
ENV write_timeout=120

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
