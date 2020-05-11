FROM stimela/ddfacet:1.3.3
MAINTAINER <sphemakh@gmail.com>
ENV GIT_LFS_SKIP_SMUDGE 1
RUN pip3 install -U pip setuptools wheel
RUN apt-get update && apt-get install -y wget git-all
RUN git clone -b decasacore300fication https://github.com/ratt-ru/CubiCal
WORKDIR CubiCal
#RUN git checkout decasacore300fication
RUN pip3 install -I ".[lsm-support,degridder-support]"
RUN DDF.py --help
RUN gocubical --help
ENV NUMBA_CACHE_DIR /tmp
ENTRYPOINT []
