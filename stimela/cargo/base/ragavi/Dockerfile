FROM stimela/meqtrees:1.2.0
RUN docker-apt-install curl
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN docker-apt-install nodejs python3-pip
RUN apt-get update
RUN pip3 install -U pip setuptools
RUN pip3 install ragavi