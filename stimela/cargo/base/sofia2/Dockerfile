FROM quay.io/stimela/base:1.7.1
RUN docker-apt-install build-essential \
        casacore-dev \
        python3 \
        python3-pip \
        wcslib-dev
RUN pip install -U setuptools \
        astro-tigger-lsm
RUN git clone https://github.com/SoFiA-Admin/SoFiA-2.git
RUN cd /SoFiA-2 && git fetch && git fetch --tags
RUN cd /SoFiA-2 && git checkout v2.5.0
RUN cd /SoFiA-2 && ./compile.sh -fopenmp
RUN cd /SoFiA-2 && ln sofia /usr/bin/sofia

