FROM quay.io/stimela/base:1.9.0
# cmake, g++ and FFTW are needed to build finufft on arm64, where PyPI has no
# wheel
RUN docker-apt-install python3-tk \
    cmake \
    g++ \
    libfftw3-dev
RUN pip install --break-system-packages --no-cache-dir RM-Tools==1.5.0 pymultinest
RUN rmsynth1d --help
RUN rmclean1d --help
RUN rmsynth3d --help
RUN rmclean3d --help
