FROM quay.io/stimela/base:1.9.0
RUN docker-apt-install texmaker \
                       dvipng \
                       python-tk \
                       python-numpy
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install sharpener
