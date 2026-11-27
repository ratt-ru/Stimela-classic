FROM quay.io/stimela/base:1.9.0
RUN docker-apt-install montage python3-montagepy
RUN pip install --break-system-packages --no-cache-dir "astroquery>=0.3.8"
RUN command -v mProject mProjectCube mAdd mImgtbl
RUN python3 -c "import MontagePy.main, astroquery"
