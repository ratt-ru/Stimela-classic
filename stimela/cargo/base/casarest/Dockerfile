FROM quay.io/stimela/base:1.9.0
# casarest (lwimager) and python-casacore come prebuilt from KERN 10 for amd64 and arm64.
RUN docker-apt-install casarest \
    casacore-data \
    python3-casacore \
    python3-astropy \
    python3-numpy \
    python3-scipy \
    python3-matplotlib
RUN pip install --break-system-packages --no-cache-dir msutils==1.2.0 dask-ms==0.2.21 "dask[array]<2024.11.0" bokeh
RUN command -v lwimager
RUN python3 -c "import MSUtils.msutils, pyrap.images, pyrap.tables, astropy.io.fits"
