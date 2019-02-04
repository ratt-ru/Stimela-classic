FROM stimela/meqtrees:1.0.1
RUN docker-apt-install curl
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN docker-apt-install nodejs
RUN pip install -U pip setuptools
RUN pip install -U backports-abc>=0.5 \
    backports.functools-lru-cache>=1.5 \
    backports.shutil-get-terminal-size>=1.0.0 \
    bokeh>=0.12.16 \
    cycler>=0.10.0 \
    futures>=3.2.0 \
    "ipykernel>=4.8.2,<5.0" \
    "ipython>=5.8.0,<6.0" \
    ipython-genutils>=0.2.0 \
    Jinja2>=2.10 \
    kiwisolver>=1.0.1 \
    MarkupSafe>=1.0 \
    "matplotlib>=2.2.3,<3.0" \
    nodeenv>=1.3.2 \
    notebook>=5.5.0 \
    numpy>=1.15.1 \
    optional-django>=0.1.0 \
    packaging>=17.1 \
    pyparsing>=2.2.0 \
    python-dateutil>=2.7.3 \
    pytz>=2018.5 \
    PyYAML>=3.13 \
    six>=1.11.0 \
    tornado>=5.1 \
    traitlets>=4.3.1
RUN pip install --no-deps ragavi
