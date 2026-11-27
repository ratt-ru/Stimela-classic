FROM quay.io/stimela/base:1.9.0
# mosaic-queen needs numpy<2, which Ubuntu's numpy 1.26 (pulled in by
# python3-montagepy) satisfies
RUN docker-apt-install montage python3-montagepy
RUN pip install --break-system-packages --no-cache-dir mosaic-queen==2.0.2 "astroquery>=0.3.8"
RUN mosaic-queen --help
