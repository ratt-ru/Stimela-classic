FROM stimela/meqtrees:1.6.3
RUN docker-apt-install python3-pip \
                       python3-numpy \
                       python3-matplotlib \
                       python3-astropy \
                       libboost-all-dev \
                       libboost-numpy-dev \
                       python3-setuptools

RUN pip3 install astroquery corner emcee pandas pyregion scikit-image tqdm

RUN git clone https://github.com/JortBox/Halo-FDCA halo-fdca-dir
RUN cd halo-fdca-dir
WORKDIR "halo-fdca-dir"
RUN git checkout v1.5
RUN ls
RUN chmod +x HaloFitting.py
RUN ln -s /halo-fdca-dir/HaloFitting.py /usr/bin/halofitting
RUN halofitting -h
