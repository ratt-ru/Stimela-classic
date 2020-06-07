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
RUN pip install scabha
RUN webdriverdownloader firefox
RUN ragavi-gains -h
RUN ragavi-vis -h
