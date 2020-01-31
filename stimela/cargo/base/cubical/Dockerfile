FROM bhugo/ddfacet:0.4.1
MAINTAINER <sphemakh@gmail.com>

RUN pip install pyyaml
RUN pip install astropy==2.0.11 -U # fixes udocker environment issue
RUN apt install xvfb -y
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99 

ENV GIT_LFS_SKIP_SMUDGE 1
RUN pip install -U pip setuptools wheel
RUN apt-get update && apt-get install -y wget git-all
RUN git clone https://github.com/ratt-ru/CubiCal
WORKDIR CubiCal
RUN git checkout 1.4.0
RUN pip install ".[lsm-support,degridder-support]"
RUN DDF.py --help
RUN gocubical --help
ENV NUMBA_CACHE_DIR /tmp

ENTRYPOINT []
