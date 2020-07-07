FROM stimela/base:1.2.5
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN apt-get update
RUN pip3 install -U pip setuptools \
    pyyaml \
    python-casacore
RUN pip install ragavi
RUN pip install numba==0.48
RUN pip install scabha
RUN ragavi-gains -h
RUN ragavi-vis -h
RUN ragavi-vis -v