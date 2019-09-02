FROM stimela/base:1.2.0
RUN docker-apt-install python-casacore \
                       xvfb \
                       texmaker \
                       dvipng \
                       python-tk

RUN pip install --upgrade pip
RUN pip install rfinder -U
RUN pip install pillow --upgrade
