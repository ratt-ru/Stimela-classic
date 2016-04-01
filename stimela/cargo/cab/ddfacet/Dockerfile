FROM radioastro/ddfacet
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ENV TERM xterm

ADD src /code
ADD tmpfs /etc/defaults/tmpfs

WORKDIR /code

CMD python run.py
