FROM stimela/meqtrees:1.0.0
RUN docker-apt-install curl
curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN docker-apt-install -y nodejs
RUN pip install -U ragavi
