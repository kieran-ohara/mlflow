FROM docker.io/tensorflow/serving:2.11.0
WORKDIR /models/model
COPY ./output ./