FROM kernsuite/base:2

RUN docker-apt-install git \
        python \
        python-pip \
        qt5-qmake \
        qt5-default \
        gfortran \
        libgfortran3 

RUN pip install numpy \
        scipy \
        matplotlib \
        astropy
RUN pip install pyyaml

RUN git clone https://github.com/SoFiA-Admin/SoFiA /build/sofia
RUN cd /build/sofia && python setup.py install

ENV SOFIA_MODULE_PATH="/build/sofia/build/lib.linux-x86_64-2.7"
ENV SOFIA_PIPELINE_PATH="/build/sofia/sofia_pipeline.py"
ENV PATH="$PATH:/build/sofia:/build/sofia/gui"




