#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="imaging_params.json"
fi

pyxis azishe -f
