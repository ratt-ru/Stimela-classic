FROM stimela/base:1.2.0
RUN docker-apt-install texmaker \
                       dvipng \
                       python-tk \
                       python-numpy
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install sharpener
