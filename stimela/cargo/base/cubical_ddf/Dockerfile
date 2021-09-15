FROM stimela/ddfacet:1.7.0
MAINTAINER <sphemakh@gmail.com>
ENV GIT_LFS_SKIP_SMUDGE 1
RUN pip3 install -U pip setuptools wheel
RUN apt-get update && apt-get install -y wget git-all
RUN git clone -b v1.5.11 https://github.com/ratt-ru/CubiCal
WORKDIR CubiCal
RUN pip3 install ".[lsm-support,degridder-support]"
RUN DDF.py --help
RUN gocubical --help
ENV NUMBA_CACHE_DIR /tmp
ENTRYPOINT []
