FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
# python-casacore, numpy, scipy and matplotlib come prebuilt from KERN 10
RUN docker-apt-install python3-casacore \
    casacore-data \
    python3-numpy \
    python3-scipy \
    python3-matplotlib
RUN pip install --break-system-packages --no-cache-dir msutils==1.2.0 dask-ms==0.2.21 "dask[array]<2024.11.0" bokeh
RUN python3 -c "import numpy, MSUtils.msutils, MSUtils.ClassESW, MSUtils.imp_plotter, MSUtils.flag_stats; assert numpy.__version__.startswith('1.'), numpy.__version__"
