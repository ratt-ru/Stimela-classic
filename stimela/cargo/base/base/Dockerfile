FROM kernsuite/base:7
RUN docker-apt-upgrade
RUN docker-apt-install \
    python3-setuptools \
    libboost-python-dev \
    python3-pip \
    git \
    xvfb \
    curl \
    wget
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN pip --version
RUN python --version
RUN pip install -U pip setuptools
RUN pip install pyyaml scabha
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
