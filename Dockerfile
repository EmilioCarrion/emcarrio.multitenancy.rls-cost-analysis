FROM python:3.8-buster

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /src

COPY Makefile .
COPY requirements.txt .

RUN make install-requirements
