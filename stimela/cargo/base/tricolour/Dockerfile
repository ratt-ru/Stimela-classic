FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python-casacore python3-pip git
RUN git clone -b 0.1.3 https://2234b98dd83a5b751cc8490e0a00cc7ca2541a84:x-oauth-basic@github.com/ska-sa/tricolour.git /tricolour
RUN pip3 install -U pip setuptools
RUN pip3 install /tricolour
