#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="caibrator_params.json"
fi

pyxis azishe -f

if [ -f "core" ]; then 
    cp core /ouput/core
fi
