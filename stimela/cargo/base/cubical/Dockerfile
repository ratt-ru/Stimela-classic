FROM stimela/ddfacet:1.7.1
RUN apt install -y \
    casacore-data
RUN . /opt/venv/bin/activate && \
    python -m pip install 'cubical[lsm-support,degridder-support]==1.6.1' 'scabha==0.3.2'
RUN DDF.py --help
RUN gocubical --help
