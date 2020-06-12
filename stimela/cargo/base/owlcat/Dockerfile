FROM stimela/base:1.4.6
RUN docker-apt-install python3-casacore \
    casacore-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install meqtrees-cattery python-casacore --upgrade
RUN pip install git+https://github.com/ska-sa/owlcat.git@issue-67
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
