FROM radioastro/base
RUN add-apt-repository -ys ppa:radio-astro/main && apt-get install -y time git

# make sure child images have latest deb package cache
ONBUILD RUN apt-get update
