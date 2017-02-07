FROM stimela/base:0.2.5
RUN docker-apt-install lofar
RUN docker-apt-install python-tigger
RUN pip install git+git://github.com/SpheMakh/tigger --upgrade
RUN apt-get install python-numpy -y
RUN apt-get install python-scipy -y
RUN apt-get install python-pyfits -y

RUN pip install astlib matplotlib
RUN pip install git+git://github.com/radio-astro/sourcery
