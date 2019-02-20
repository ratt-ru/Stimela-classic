FROM stimela/meqtrees:1.0.1
RUN docker-apt-install curl
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN docker-apt-install nodejs
RUN pip install -U pip setuptools
RUN pip install ragavi
