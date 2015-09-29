FROM radioastro/base
RUN apt-get update && apt-get install -y \
    casarest \
    wsclean \
    python-pyxis

ADD . /code
WORKDIR /code

CMD ./run.sh
