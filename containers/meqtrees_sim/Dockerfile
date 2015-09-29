FROM radioastro/base
RUN apt-get update
RUN apt-get install -y meqtrees python-pyxis

ADD . /code
WORKDIR /code

CMD ./run.sh


