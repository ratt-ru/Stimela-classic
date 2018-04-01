FROM stimela/base:0.3.2
RUN docker-apt-install libfreetype6-dev \
        wcslib-dev libcfitsio-dev \ 
        python-casacore
RUN pip install -U pip setuptools wheel virtualenv
RUN pip install numpy matplotlib futures scipy scipy progress
RUN pip install -I politsiyakat>=0.3.7
