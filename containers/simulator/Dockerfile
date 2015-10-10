FROM penthesilea/base
MAINTAINER sphemakh@gmail.com

RUN apt-get build-dep meqtrees-timba -y && apt-get install meqtrees -y

ENV USER root

ADD src /code

RUN mkdir /output

WORKDIR /code

CMD ./run.sh
