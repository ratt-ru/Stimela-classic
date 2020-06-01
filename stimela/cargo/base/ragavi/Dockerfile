FROM stimela/base:1.2.5
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN add-apt-repository ppa:mozillateam/ppa
RUN apt-get update
RUN apt-get install -y firefox
RUN pip3 install -U pip setuptools \
    pyyaml \
    python-casacore \
    ragavi \
    selenium \
    webdriverdownloader
RUN pip3 install -I numpy
# so we can use use e.g. docker build --build-arg SCABHA=git+https://github.com/ratt-ru/scabha.git@branch to
# install from a dev version, instead of a release package
ARG SCABHA=scabha
RUN pip install $SCABHA
RUN webdriverdownloader firefox
RUN ragavi-gains -h
RUN ragavi-vis -h
