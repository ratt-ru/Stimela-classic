FROM stimela/base:1.2.5
RUN docker-apt-install \
    python3-setuptools \
    python3-pip \
    git \
    xvfb \
    curl \
    wget \
    casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install --upgrade --force pip
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN pip install -U pip setuptools "python-casacore<=3.0.0"
RUN pip install -I ragavi>=0.3.5
RUN pip install --force-reinstall -U git+https://github.com/o-smirnov/datashader
RUN pip install -I numpy
RUN ragavi-gains -h
RUN ragavi-vis -h
