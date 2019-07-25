FROM stimela/base:1.0.1
RUN docker-apt-install meqtrees time
RUN pip install -U pip setuptools
RUN pip install astropy pywcs
RUN pip install -U owlcat>=1.5.3
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
