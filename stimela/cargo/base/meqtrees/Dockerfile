FROM stimela/base:1.0.1
RUN docker-apt-install meqtrees time
RUN pip install -U pip setuptools
RUN pip install astropy pywcs
RUN pip install -U git+https://github.com/ska-sa/owlcat
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
