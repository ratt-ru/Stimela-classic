FROM stimela/base:1.0.0
RUN docker-apt-install libfreetype6-dev \
        wcslib-dev libcfitsio-dev \ 
        python-casacore
RUN pip install -U pip setuptools wheel virtualenv
RUN pip install numpy matplotlib futures scipy scipy progress
RUN pip install --no-deps politsiyakat>=0.3.7
