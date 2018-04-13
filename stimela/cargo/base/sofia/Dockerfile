FROM stimela/base:1.0.0

RUN docker-apt-install python \
        qt5-qmake \
        qt5-default \
        gfortran \
        libgfortran3 

RUN pip install numpy \
        scipy \
        matplotlib \
        astropy

RUN git clone https://github.com/SoFiA-Admin/SoFiA /build/sofia
RUN cd /build/sofia && git checkout tags/v1.1.0 && python setup.py install 

ENV SOFIA_MODULE_PATH="/build/sofia/build/lib.linux-x86_64-2.7"
ENV SOFIA_PIPELINE_PATH="/build/sofia/sofia_pipeline.py"
ENV PATH="$PATH:/build/sofia:/build/sofia/gui"




