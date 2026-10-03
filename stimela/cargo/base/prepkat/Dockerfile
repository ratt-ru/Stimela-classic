FROM quay.io/stimela/base:1.8.0

RUN docker-apt-install \
	build-essential \
	casacore-data \
	casacore-dev \
	git \
	libboost-python-dev \
	libpython3-dev \
	pkg-config

RUN pip3 install --break-system-packages --no-cache-dir \
	"rich==12.6.0" \
	"git+https://github.com/JSKenyon/PrepKAT.git"

RUN katflip --help
