FROM quay.io/stimela/base:1.9.0
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
    locales \
    casacore-data
ENV DIRCASA /casa
RUN mkdir $DIRCASA
ENV CASA_VERSION casa-release-5.8.0-109.el7
ENV SUCASA ${DIRCASA}/${CASA_VERSION}
ENV CASAURL https://casa.nrao.edu/download/distro/casa/release/el7/casa-release-5.8.0-109.el7.tar.gz
RUN curl -L -o ${SUCASA}.tar.gz $CASAURL
RUN tar xvf ${SUCASA}.tar.gz -C $DIRCASA
RUN rm ${SUCASA}.tar.gz
ENV PATH $PATH:${SUCASA}/bin
# simms 2.x needs casatools. casatools 6.7.6 bundles a libssl that needs a newer
# OpenSSL than Ubuntu 24.04 has, so stay on 6.7.5. casatools/simms only exist
# for x86_64.
RUN pip install --break-system-packages git+https://github.com/SpheMakh/crasa.git python-casacore astropy \
    "simms<3" casatools==6.7.5.18 casatasks==6.7.5.18
# Point casatools at the casacore-data measures, without auto-updates, for any
# user and HOME
RUN printf 'measurespath = "/usr/share/casacore/data"\nmeasures_auto_update = False\ndata_auto_update = False\n' \
    > /usr/local/lib/python3.12/dist-packages/casasiteconfig.py
RUN python -c "import Crasa.Crasa"
RUN python3 -c "from casatools import ms, simulator, measures, image"
RUN simms --help
ENV LANGUAGE  en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL  en_US.UTF-8
RUN locale-gen en_US.UTF-8
#RUN casa --nologger --log2term --help --nogui
