FROM quay.io/stimela/base:1.7.1
RUN docker-apt-install python3-pip \
                       python3-numpy \
                       python3-matplotlib \
                       gfortran \
                       python-dev \
                       libboost-all-dev \
                       libboost-python-dev \
                       libboost-numpy-dev \
                       python3-setuptools \
                       pybdsf

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN pip3 install -U pip bdsf
RUN pip3 install aimfast
