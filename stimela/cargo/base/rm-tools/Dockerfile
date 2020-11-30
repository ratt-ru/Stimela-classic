FROM stimela/base:1.6.0
RUN docker-apt-install python3-tk
RUN pip install RM-Tools pymultinest "git+https://github.com/ratt-ru/scabha@local-prefix"
RUN rmsynth1d --help
RUN rmclean1d --help
RUN rmsynth3d --help
RUN rmclean3d --help
#RUN qufit --help
