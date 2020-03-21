FROM stimela/base:1.2.4
RUN docker-apt-install python3-casacore python3-pip
RUN pip3 install git+https://github.com/IanHeywood/shadeMS.git@dbcd2b8592eb2d0d1fa63a4d46d579d7af96bb69#egg=shadems
RUN shadems -h
