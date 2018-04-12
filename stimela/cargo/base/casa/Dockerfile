FROM stimela/casa:0.3.2
RUN docker-apt-install git locales
RUN locale-gen en_US.UTF-8
RUN pip install -U pip 
RUN pip install -U drive-casa pyyaml
RUN pip install -U git+https://github.com/SpheMakh/crasa.git
