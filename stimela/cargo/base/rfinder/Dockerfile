FROM quay.io/stimela/base:1.8.0
RUN docker-apt-install python3-casacore \
                       xvfb \
                       texmaker \
                       dvipng \
                       python-tk
                       python3-tk

RUN docker-apt-install python3.12-venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade setuptools pip
RUN pip install rfinder pillow -U
