FROM quay.io/stimela/base:1.9.0
RUN docker-apt-install libfreetype6-dev \
        wcslib-dev libcfitsio-dev \ 
        python-casacore
RUN pip install -U pip setuptools wheel virtualenv
RUN pip install -U politsiyakat>=0.3.7
