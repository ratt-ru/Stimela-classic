#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="imaging_params.json"
fi


RAN_OPERATION=$(python run.py)

if [ "$RAN_OPERATION" = "no" ]; then
    pyxis azishe -f
else
    echo ""
fi
