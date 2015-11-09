FROM penthesilea/autoflagger:stable.11.15
MAINTAINER <sphemakh@gmial.com>

RUN mkdir -p /input /output

ADD src /code

WORKDIR /code

CMD python run.py
