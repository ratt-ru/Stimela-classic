FROM stimela/meqtrees:1.2.0
RUN docker-apt-install curl
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN docker-apt-install nodejs python3-pip
RUN add-apt-repository ppa:git-core/ppa
RUN apt-get update
RUN apt-get install -y git
RUN pip3 install -U pip setuptools
RUN pip3 install ragavi
RUN pip3 install git+git://github.com/ska-sa/xova.git@master