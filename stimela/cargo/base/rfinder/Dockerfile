FROM stimela/base:1.0.0
RUN docker-apt-install casacore-dev \
                       python-casacore \
                       xvfb \
                       texmaker \
                       dvipng \
                       python-tk

RUN pip install --upgrade pip
RUN git clone https://github.com/Fil8/RFInder /build/rfinder
RUN cd /build/rfinder && git checkout 1.0.0 && pip install .
