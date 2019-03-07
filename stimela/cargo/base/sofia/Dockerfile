FROM stimela/base:1.0.0

RUN docker-apt-install python \
        qt5-qmake \
        qt5-default \
        gfortran \
        libgfortran3 

RUN pip install numpy \
        scipy \
        matplotlib \
        astropy \
        astro-tigger-lsm

RUN git clone https://github.com/SoFiA-Admin/SoFiA.git /sofia
RUN cd /sofia && git fetch && git fetch --tags
RUN cd /sofia && git checkout v1.2.0
RUN cd /sofia && python setup.py  install
ENV SOFIA_MODULE_PATH /sofia/build/lib.linux-x86_64-2.7
ENV SOFIA_PIPELINE_PATH /sofia/sofia_pipeline.py
ENV PATH $PATH:/sofia:/sofia/gui
RUN echo $PATH
