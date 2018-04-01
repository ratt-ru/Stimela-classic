FROM stimela/base:0.3.2
RUN docker-apt-install meqtrees time
RUN pip install astropy pywcs
RUN pip install --upgrade git+https://github.com/ska-sa/owlcat
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
RUN pip install --upgrade git+https://github.com/ska-sa/meqtrees-cattery
ENV MEQTREES_CATTERY_PATH /usr/local/lib/python2.7/dist-packages/Cattery
