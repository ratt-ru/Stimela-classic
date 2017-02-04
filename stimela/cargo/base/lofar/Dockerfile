FROM stimela/base:0.2.5
RUN docker-apt-install lofar python-tigger
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
RUN pip uninstall -y numpy
RUN pip install --upgrade pyfits numpy==1.11.3
