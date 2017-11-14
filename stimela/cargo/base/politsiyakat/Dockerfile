FROM stimela/base:0.3.1
RUN docker-apt-install libfreetype6-dev
RUN docker-apt-install wcslib-dev libcfitsio-dev
RUN docker-apt-install python-casacore
RUN pip install pip setuptools wheel virtualenv -U
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/
#RUN pip install git+http://github.com/bennahugo/politsiyakat.git
RUN pip install politsiyakat==0.3.7
