#!make

PROJECT=penthesilea
INPUT=`pwd`/input
OUTPUT=`pwd`/output
CONFIGS=/input/configs

SIMMS="simms_`date +%d%m%y_%H%M`"
SIMULATOR="simulator_`date +%d%m%y_%H%M`"
IMAGER="imager_`date +%d%m%y_%H%M`"

LOG=.active_containers.txt

ifndef config
    config=input/configs/driver.json
endif


.PHONY: all build force-build run stop kill

all: build run stop kill

build:
		./azishe.py -c $(config) -in "/data" -out "/output" -p $(PROJECT)
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/simulator containers/simulator
		docker build -t $(PROJECT)/imager containers/imager

force-build:
		docker build -t $(PROJECT)/base --no-cache=true containers/base
		docker build -t $(PROJECT)/simms --no-cache=true containers/simms
		docker build -t $(PROJECT)/simulator --no-cache=true containers/simulator
		docker build -t $(PROJECT)/imager --no-cache=true containers/imager

pull-images:
		./azishe.py -c $(config) -in "/data" -out "/output" -p $(PROJECT)
		docker pull $(PROJECT)/base
		docker pull $(PROJECT)/simms
		docker pull $(PROJECT)/simulator
		docker pull $(PROJECT)/imager
        
run:
		echo $(SIMMS) >> $(LOG) && \
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(CONFIGS)/$(PROJECT)-simms_params.json --name $(SIMMS) $(PROJECT)/simms && \
		head $(LOG) -n -1 > .temp-$(LOG) && mv .temp-$(LOG) $(LOG) && \
		echo $(SIMULATOR) >> $(LOG) && \
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(CONFIGS)/$(PROJECT)-simulator_params.json --name $(SIMULATOR) $(PROJECT)/simulator && \
		head $(LOG) -n -1 > .temp-$(LOG) && mv .temp-$(LOG) $(LOG) && \
		echo $(IMAGER) >> $(LOG) && \
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(CONFIGS)/$(PROJECT)-imager_params.json --name $(IMAGER) $(PROJECT)/imager && \
		head $(LOG) -n -1 > .temp-$(LOG) && mv .temp-$(LOG) $(LOG)

stop:
		test -s $(LOG) && cat $(LOG) | xargs docker stop ; touch $(LOG)

kill:
		test -s $(LOG) && cat $(LOG) | xargs docker kill ; touch $(LOG)
