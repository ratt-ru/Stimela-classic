FROM sphemakh/crasa:5.6.1
RUN docker-apt-install python3-casacore python3 python3-pip git wget xvfb
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.5 10
RUN pip3 install --upgrade --force pip
RUN pip install -U pip 
RUN pip install -U crasa pyyaml astropy

# so we can use use e.g. docker build --build-arg SCABHA=git+https://github.com/ratt-ru/scabha.git@branch to
# install from a dev version, instead of a release package
ARG SCABHA=scabha
RUN pip install $SCABHA
