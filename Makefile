#!make

PROJECT=penthesilea
INPUT=`pwd`/input
OUTPUT=`pwd`/output
CONFIGS=/input/configs

LOG=`pwd`/src/.$(PROJECT).log

ifndef config
    config=driver.json
endif

config_=input/configs/$(config)
DRIVER=`pwd`/src/azishe.py

.PHONY: all build force-build run stop kill

all: build run stop kill

build:  
		touch $(LOG)
		$(DRIVER) -c $(config_) -in $(INPUT) -out $(OUTPUT) -p $(PROJECT) -ts `date +%d%m%y_%H%M`
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/casapy containers/casapy
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/simulator containers/simulator
		docker build -t $(PROJECT)/predict containers/predict
		docker build -t $(PROJECT)/imager containers/imager
		docker build -t $(PROJECT)/sourcery containers/sourcery

force-build:
		touch $(LOG)
		$(DRIVER) -c $(config_) -in $(INPUT) -out $(OUTPUT) -p $(PROJECT) -ts `date +%d%m%y_%H%M`
		docker build -t $(PROJECT)/base --no-cache=true containers/base
		docker build -t $(PROJECT)/casapy --nocache=true containers/casapy
		docker build -t $(PROJECT)/simms --no-cache=true containers/simms
		docker build -t $(PROJECT)/simulator --no-cache=true containers/simulator
		docker build -t $(PROJECT)/predict --no-cache=true containers/predict
		docker build -t $(PROJECT)/imager --no-cache=true containers/imager
		docker build -t $(PROJECT)/sourcery --no-cache=true containers/sourcery

pull-images:
		touch $(LOG)
		$(DRIVER) -c $(config_) -in $(INPUT) -out $(OUTPUT) -p $(PROJECT) -ts `date +%d%m%y_%H%M`
		docker pull $(PROJECT)/base
		docker pull $(PROJECT)/simms
		docker pull $(PROJECT)/simulator
		docker pull $(PROJECT)/predict
		docker pull $(PROJECT)/imager
		docker pull $(PROJECT)/sourcery
        
run:
		bash `pwd`/src/run.sh
stop:
		`pwd`/src/logger.py $(LOG) all stop

kill:
		`pwd`/src/logger.py $(LOG) all rm
