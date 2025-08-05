FROM quay.io/stimela/base:1.7.1
RUN docker-apt-install montage python3-montagepy vim
# Install Python 3.10
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils python3.10-venv

# Update alternatives to use Python 3.10
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 10 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.10 10

# Create a virtual environment for Python 3.10
RUN python3.10 -m venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools
RUN pip install -U mosaic-queen astroquery>=0.3.8 scabha==0.3.2
RUN pip show mosaic-queen
RUN mosaic-queen --help
