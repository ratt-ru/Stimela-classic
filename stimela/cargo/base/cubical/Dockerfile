FROM stimela/base:0.3.1
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install python-casacore python-tigger
RUN git clone https://github.com/ratt-ru/CubiCal.git /builds/CubiCal
RUN pip install -r /builds/CubiCal/requirements.txt
RUN pip install /builds/CubiCal
RUN rm -fr /builds/CubiCal
RUN pip install -U pip setuptools wheel
RUN pip install git+git://github.com/ska-sa/montblanc.git@master
