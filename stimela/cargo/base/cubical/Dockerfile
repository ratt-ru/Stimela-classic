FROM quay.io/stimela/ddfacet:1.7.1
RUN apt install -y \
    casacore-data
RUN . /opt/venv/bin/activate && \
    #python -m pip install 'cubical[lsm-support,degridder-support]==1.6.3' 'scabha==0.3.2'
    python -m pip install git+https://github.com/ratt-ru/CubiCal.git scabha==0.3.2
RUN DDF.py --help
RUN gocubical --help
