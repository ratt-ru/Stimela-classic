FROM stimela/base:1.0.1
ADD . /Stimela
WORKDIR /Stimela
RUN pip install -U pip
RUN pip install /Stimela
ENV USER root
RUN stimela
