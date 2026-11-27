FROM quay.io/stimela/ddfacet:1.9.0
RUN python3 -m pip install --break-system-packages --no-cache-dir \
    git+https://github.com/ratt-ru/CubiCal.git@py312-numpy2
RUN DDF.py --help
RUN gocubical --help
