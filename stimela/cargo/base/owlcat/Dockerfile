FROM quay.io/stimela/base:1.9.0
# Cattery and casacore come prebuilt from KERN 10 for amd64 and arm64
RUN docker-apt-install python3-meqtrees-cattery \
    casacore-data \
    python3-matplotlib \
    python3-six
# --no-deps keeps pip from replacing the KERN python-casacore/Cattery
RUN pip install --break-system-packages --no-cache-dir --no-deps owlcat==1.8.1 && \
    pip install --break-system-packages --no-cache-dir bokeh
RUN python3 -c "import Owlcat, Cattery, pyrap.tables"
RUN flag-ms.py --help
RUN fitstool.py --help
RUN plot-elevation-tracks.py --help
