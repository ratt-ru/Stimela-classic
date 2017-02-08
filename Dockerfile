FROM stimela/base
ADD . /Stimela
WORKDIR /Stimela
RUN pip install /Stimela
ENV USER root
RUN stimela
