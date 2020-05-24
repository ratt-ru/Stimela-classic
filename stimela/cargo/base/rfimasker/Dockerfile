FROM stimela/base:1.2.0
RUN docker-apt-install python-numpy python-casacore
RUN pip install -U numpy scipy python-casacore
RUN pip install --no-deps git+https://github.com/bennahugo/RFIMasker

# so we can use use e.g. docker build --build-arg SCABHA=git+https://github.com/ratt-ru/scabha.git@branch to
# install from a dev version, instead of a release package
ARG SCABHA=scabha
RUN pip install $SCABHA

