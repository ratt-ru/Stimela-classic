FROM stimela/base:1.6.0
ENV DIRCASA /casa
RUN mkdir $DIRCASA
#ENV CASA_VERSION casa-release-5.6.0-60.el7
ENV CASA_VERSION casa-pipeline-release-5.6.1-8.el7
ENV SUCASA ${DIRCASA}/${CASA_VERSION}
ENV CASAURL https://casa.nrao.edu/download/distro/casa-pipeline/release/el7/casa-pipeline-release-5.6.1-8.el7.tar.gz
#ENV CASAURL https://casa.nrao.edu/download/distro/casa/release/el7/${CASA_VERSION}.tar.gz
RUN curl -L -o ${SUCASA}.tar.gz $CASAURL
RUN tar xzvf ${SUCASA}.tar.gz -C $DIRCASA
RUN rm ${SUCASA}.tar.gz
ENV PATH $PATH:${SUCASA}/bin
RUN docker-apt-install libfreetype6 \
    libsm6 \
    libxi6 \
    libxrender1 \
    libxrandr2 \
    libxfixes3 \
    libxcursor1 \
    libxinerama1 \
    libfontconfig1 \
    libxslt1.1 \
    xauth \
    xvfb \
    dbus-x11 \
    python-tk \
    apt-utils \
    locales 
RUN pip install scabha crasa python-casacore astropy
RUN python -c "import Crasa.Crasa"
ENV LANGUAGE  en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL  en_US.UTF-8
RUN locale-gen en_US.UTF-8
RUN casa --nologger --log2term --help
