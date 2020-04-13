FROM stimela/base:1.2.0
RUN docker-apt-install python \
        qt5-qmake \
        qt5-default \
        gfortran \
        libgfortran3 \
        gcc \
        zlib1g \
        zlib1g-dev
RUN pip install -U numpy>=1.8 \
        scipy>=0.7 \
        matplotlib>=1.1 \
        astropy>=0.2.5 \
        astro-tigger-lsm
RUN git clone https://github.com/SoFiA-Admin/SoFiA.git /sofia
RUN cd /sofia && git fetch && git fetch --tags
RUN cd /sofia && git checkout v1.3.2
RUN cd /sofia && python setup.py  install
ENV SOFIA_MODULE_PATH /sofia/build/lib.linux-x86_64-2.7
ENV SOFIA_PIPELINE_PATH /sofia/sofia_pipeline.py
ENV PATH $PATH:/sofia:/sofia/gui
RUN echo $PATH
#RUN sed -i 's/from sofia import wavelet_finder/# from sofia import wavelet_finder/g' $SOFIA_PIPELINE_PATH
#RUN cat $SOFIA_PIPELINE_PATH
