FROM radioastro/meqtrees
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ADD src /code
WORKDIR /code

ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery

CMD python run.py
