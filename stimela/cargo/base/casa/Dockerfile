FROM stimela/base:1.6.0
ENV SUCASA /casa-pipeline-release-5.6.1-8.el7
ENV DIRCASA /casa
RUN mkdir $DIRCASA
ENV CASAURL https://casa.nrao.edu/download/distro/casa-pipeline/release/el7/casa-pipeline-release-5.6.1-8.el7.tar.gz
RUN curl -L -o ${SUCASA}.tar.gz $CASAURL
RUN tar xzvf ${SUCASA}.tar.gz -C $DIRCASA
RUN rm ${SUCASA}.tar.gz
ENV PATH $PATH:/casa/casa-pipeline-release-5.6.1-8.el7/bin
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
RUN pip install scabha crasa
RUN python -c "import Crasa.Crasa"
RUN casa --nologger --log2term --help
