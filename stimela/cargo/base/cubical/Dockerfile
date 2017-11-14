FROM stimela/cubical:dev
MAINTAINER <sphemakh@gmail.com>
#RUN docker-apt-install python-pip git python-casacore python-tigger
#RUN pip install -U pip setuptools wheel cython>=0.25.2
#RUN pip install -I git+git://github.com/ska-sa/montblanc.git@master

RUN git clone -b only-dd-fixes https://github.com/ratt-ru/CubiCal.git /cubical
RUN pip install --no-deps -U /cubical
