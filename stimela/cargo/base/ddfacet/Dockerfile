FROM stimela/base:0.3.1

ENV DEB_DEPENCENDIES \
    virtualenv \
    python-pip \
    libfftw3-dev \
    casacore-data \
    casacore-dev \
    python-numpy \
    libfreetype6 \
    libfreetype6-dev \
    libpng12.0 \
    libpng12-dev \
    pkg-config \
    python2.7-dev \
    libboost-all-dev \
    libcfitsio3-dev \
    wcslib-dev \
    libatlas-dev \
    liblapack-dev \
    python-tk \
    meqtrees*

RUN apt-get update && \
    #apt-get install -y software-properties-common && \
    #add-apt-repository -y -s ppa:kernsuite/kern-2 && \
    #apt-add-repository -y multiverse && \
    #apt-get update && \
    apt-get install -y $DEB_DEPENCENDIES && \
    # Virtual environment and upgrades
    virtualenv --system-site-packages /ddfvenv && \
    . /ddfvenv/bin/activate && \
    pip install -U pip virtualenv setuptools wheel && \
    # Install the latest wheel for DDFacet
    pip install --force-reinstall DDFacet && \
    # TODO: in future pip install the requirements file when I include it with the source bundle
    pip install "git+https://github.com/ska-sa/montblanc.git@65ffb611f5" && \
    pip install "pymoresane == 0.3.0" && \
    # Nuke the unused & cached stuff
    apt-get autoclean -y && \
    apt-get clean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/ && \
    rm -rf /var/cache/

ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
ENV PATH /ddfvenv/bin:$PATH
ENV LD_LIBRARY_PATH /ddfvenv/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH /usr/lib/python2.7/dist-packages/Cattery:$PYTHONPATH

# Execute virtual environment version of DDFacet
ENTRYPOINT ["DDF.py"]
CMD ["--help"]
