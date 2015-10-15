#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="simms_params.json"
fi

python fitsinfo.py
simms -jc $CONFIG
