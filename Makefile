#!make

PROJECT=penthesilea

.PHONY: all build pull

all: pull

build:  
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/casapy containers/casapy
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/meqtrees containers/meqtrees
		docker build -t $(PROJECT)/imager containers/imager
		docker build -t $(PROJECT)/sourcery containers/sourcery

pull:
		docker pull $(PROJECT)/base:stable.11.15
		docker pull $(PROJECT)/casapy:stable.11.15
		docker pull $(PROJECT)/simms:stable.11.15
		docker pull $(PROJECT)/meqtrees:stable.11.15
		docker pull $(PROJECT)/imager:stable.11.15
		docker pull $(PROJECT)/sourcery:stable.11.15
