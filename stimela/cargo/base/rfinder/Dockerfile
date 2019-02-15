FROM stimela/base:1.0.0

RUN pip install python-casacore 

RUN git clone https://github.com/Fil8/RFInder /build/rfinder
RUN cd /build/rfinder && git checkout origin/v1.0.0 && python setup.py install 
