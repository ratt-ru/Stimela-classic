FROM quay.io/stimela/base:1.9.0

# MeqTrees (Timba + Cattery), casacore and friends come prebuilt from KERN 10
# for both amd64 and arm64
RUN docker-apt-install \
    meqtrees \
    meqtrees-timba \
    makems \
    casarest \
    casacore-data \
    python3-matplotlib \
    python3-six

# Owlcat isn't packaged in KERN 10. --no-deps keeps pip from replacing the
# KERN python-casacore/Cattery with PyPI copies.
RUN pip install --break-system-packages --no-cache-dir --no-deps owlcat && \
    pip install --break-system-packages --no-cache-dir bokeh

# basic install tests
RUN python3 -c "import Cattery, Owlcat, pyrap.tables; from Cattery import Siamese, Calico"
RUN meqtree-pipeliner.py --help
RUN flag-ms.py --help
