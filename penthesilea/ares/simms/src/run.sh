#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="simms_params.json"
fi

python decide.py temp.json
simms -jc temp.json
