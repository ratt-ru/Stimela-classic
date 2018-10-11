FROM stimela/base:1.0.0
ADD . /Stimela
WORKDIR /Stimela
RUN pip install /Stimela
ENV USER root
