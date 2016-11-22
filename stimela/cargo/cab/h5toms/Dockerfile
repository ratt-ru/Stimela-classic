FROM cabb/katdal
MAINTAINER <sphemakh@gmail.com>

ADD src /code
RUN mkdir -p /input /output

WORKDIR /code

ENTRYPOINT ["python", "run.py"]