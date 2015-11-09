FROM penthesilea/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-get build-dep meqtrees-timba -y && apt-get install meqtrees -y

RUN mkdir /builds
RUN git clone https://github.com/ska-sa/tigger /builds/tigger
RUN git clone https://github.com/ska-sa/owlcat /builds/owlcat
RUN git clone -b devel https://github.com/ska-sa/meqtrees-cattery /builds/cattery
RUN cd /builds/tigger && python setup.py install
RUN cd /builds/owlcat && python setup.py install
RUN cd /builds/cattery && python setup.py install

ENV USER root
