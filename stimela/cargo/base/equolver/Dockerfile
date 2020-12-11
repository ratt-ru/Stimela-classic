FROM stimela/base:1.6.0
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN apt-get update
RUN pip3 install -U pip setuptools \
    pyyaml
RUN pip install scabha
RUN pip install -I equolver==0.0.8
RUN pip install https://www.astro.rug.nl/software/kapteyn/kapteyn-3.0.tar.gz
RUN equolver -h -v
