FROM stimela/base:1.6.0
RUN docker-apt-install python3-casacore \
    casacore-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install -U meqtrees-cattery "python-casacore>=3.3.1" "owlcat>=1.6.3" scabha future-fstrings
ENV MEQTREES_CATTERY_PATH /usr/local/lib/python3.6/dist-packages/Cattery
