FROM quay.io/stimela/base:1.9.0
# All sunblocker dependencies come prebuilt from KERN 10 / Ubuntu for amd64
# and arm64; --no-deps keeps pip from replacing them with PyPI copies
RUN docker-apt-install python3-casacore \
    casacore-data \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-astropy \
    python3-ephem
RUN pip install --break-system-packages --no-cache-dir --no-deps sunblocker==1.0.1
RUN python3 -c "import sunblocker.sunblocker"
