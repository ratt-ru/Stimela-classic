FROM stimela/base:0.3.1
MAINTAINER <sphemakh@gmail.com>
ADD sunblocker-src /sunblocker
RUN docker-apt-install python-casacore python-tk
RUN pip install -I /sunblocker
