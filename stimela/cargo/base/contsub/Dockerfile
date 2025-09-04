FROM ubuntu:24.04
RUN apt update 
RUN apt dist-upgrade -y
RUN apt install -y python3-setuptools \
    libboost-python-dev \
    python3-pip \
    git \
    xvfb \
    curl \
    wget \ 
    python-is-python3 \
    python3-full \
    pipx

ENV STIMELA_VENV="/venv"
ENV STIMELA_VENV_BIN="${STIMELA_VENV}/bin"
RUN python -m venv $STIMELA_VENV
ENV PATH="${STIMELA_VENV_BIN}/:$PATH"

RUN $STIMELA_VENV_BIN/pip install "contsub>=1.0.5"
