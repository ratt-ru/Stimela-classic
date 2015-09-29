FROM radioastro/base
RUN apt-get update
RUN apt-get install -y lwimager python-pyxis

ADD . /code
WORKDIR /code

CMD ./run.sh
