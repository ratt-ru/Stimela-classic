FROM stimela/base:1.7.1
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
    python3-tk \
    apt-utils \
    locales 
ENV DIRCASA /casa
RUN mkdir $DIRCASA
ENV CASA_VERSION casa-release-5.8.0-109.el7
ENV SUCASA ${DIRCASA}/${CASA_VERSION}
ENV CASAURL https://alma-dl.mtk.nao.ac.jp/ftp/casa/distro/casa/release/el7/casa-release-5.8.0-109.el7.tar.gz
RUN curl -L -o ${SUCASA}.tar.gz $CASAURL
RUN tar xvf ${SUCASA}.tar.gz -C $DIRCASA
RUN rm ${SUCASA}.tar.gz
ENV PATH $PATH:${SUCASA}/bin
RUN pip install git+https://github.com/SpheMakh/crasa.git python-casacore astropy git+https://github.com/ratt-ru/simms.git
RUN python -c "import Crasa.Crasa"
ENV LANGUAGE  en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL  en_US.UTF-8
RUN locale-gen en_US.UTF-8
#RUN casa --nologger --log2term --help --nogui
