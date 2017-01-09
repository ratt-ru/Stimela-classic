FROM stimela/base
RUN apt-get -y install  software-properties-common
RUN add-apt-repository -y -s ppa:kernsuite/kern-1
RUN apt-add-repository -y multiverse
RUN apt-get update
RUN apt-get install -y casarest python-pyxis
