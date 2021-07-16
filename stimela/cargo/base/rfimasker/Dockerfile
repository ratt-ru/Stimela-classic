FROM stimela/base:1.2.5
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install -U --force pip
RUN docker-apt-install python-numpy python-casacore
RUN pip install -U numpy scipy python-casacore
RUN pip install --no-deps git+https://github.com/SpheMakh/RFIMasker@master
ARG SCABHA=scabha
RUN pip install $SCABHA

