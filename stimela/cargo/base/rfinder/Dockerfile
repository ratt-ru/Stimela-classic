FROM stimela/base:1.0.0

RUN docker-apt-install casacore-dev \
		       python-casacore

RUN pip install --upgrade pip
RUN pip install matplotlib==2.2.3

RUN git clone https://github.com/Fil8/RFInder /build/rfinder
RUN cd /build/rfinder && git checkout origin/file_arranger && pip install .
