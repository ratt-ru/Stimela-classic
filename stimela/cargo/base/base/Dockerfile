FROM kernsuite/base:dev
RUN docker-apt-upgrade
RUN docker-apt-install \
    python3-setuptools \
    libboost-python-dev \
    python3-pip \
    git \
    xvfb \
    curl \
    wget
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip --version
RUN python --version
RUN pip install --upgrade --ignore-installed pip setuptools --break-system-packages
RUN pip install --break-system-packages pyyaml scabha==0.3.2
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
