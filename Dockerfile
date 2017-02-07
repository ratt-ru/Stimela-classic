FROM stimela/base
ADD . /Stimela
WORKDIR /Stimela
RUN pip install /Stimela
