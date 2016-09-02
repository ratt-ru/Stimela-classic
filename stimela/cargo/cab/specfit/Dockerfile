FROM radioastro/tigger
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery

ADD src /code
WORKDIR /code

CMD python run.py
