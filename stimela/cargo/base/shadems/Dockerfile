FROM stimela/base:1.2.4
RUN docker-apt-install python3-casacore python3-pip
RUN pip3 install git+https://github.com/ratt-ru/shadeMS.git@v0.3.0#egg=shadems
RUN pip3 install git+https://github.com/o-smirnov/datashader
RUN shadems -h