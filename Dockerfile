FROM stimela/base:0.2.9
ADD . /Stimela
WORKDIR /Stimela
RUN pip install /Stimela
ENV USER root
RUN stimela
