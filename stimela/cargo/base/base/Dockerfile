FROM kernsuite/base:dev
RUN docker-apt-install \
    python3-setuptools \
    libboost-python-dev \
    python3-pip \
    git \
    xvfb \
    curl \
    wget
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install --upgrade --force pip
RUN pip install -U pip setuptools
RUN pip install pyyaml
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
