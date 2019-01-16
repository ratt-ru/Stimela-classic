FROM stimela/casa:1.0.1
RUN docker-apt-install locales \
    casalite \
    python-pip \
    git
RUN locale-gen en_US.UTF-8
RUN pip install -U pip 
RUN pip install crasa pyyaml
RUN casa-config --exec update-data
