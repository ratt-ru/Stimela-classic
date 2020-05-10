FROM stimela/ddfacet:1.3.3
MAINTAINER <sphemakh@gmail.com>
RUN apt update && apt install -y wget git-all
ENV GIT_LFS_SKIP_SMUDGE 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install --upgrade --force pip
RUN pip install -U pip setuptools wheel
RUN git clone https://github.com/ratt-ru/CubiCal.git
WORKDIR CubiCal
RUN git checkout v1.5.2
RUN pip install ".[lsm-support,degridder-support]"
RUN DDF.py --help
RUN gocubical --help
ENV NUMBA_CACHE_DIR /tmp
ENTRYPOINT []
