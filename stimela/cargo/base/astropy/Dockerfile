FROM quay.io/stimela/base:1.9.0
RUN pip install --break-system-packages --no-cache-dir astropy numpy scipy scikit-image
# cleanmask (archived upstream) still uses pkg_resources, which current
# setuptools no longer ships, and gives its license as a list, which current
# setuptools rejects; patch both
RUN git clone https://github.com/SpheMakh/cleanmask.git /src/cleanmask && \
    cd /src/cleanmask && git checkout ab1a4dfbc66ca808596f986b0402b3b85deb33b3 && \
    sed -i -e 's/^import pkg_resources$/from importlib.metadata import version as _pkg_version/' \
        -e 's/^__version__ = pkg_resources.require("cleanmask")\[0\].version$/__version__ = _pkg_version("cleanmask")/' \
        cleanmask/CleanMask.py && \
    sed -i "s/^      license=\['GNU GPL v2'\],$/      license='GNU GPL v2',/" setup.py && \
    ! grep -q pkg_resources cleanmask/CleanMask.py && \
    pip install --break-system-packages --no-cache-dir . && \
    rm -rf /src/cleanmask
RUN cleanmask --help
