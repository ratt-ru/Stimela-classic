#!/bin/bash -ve

if [ -z "$2" ]; then 
    CONFIG="$2"
else
    CONFIG="imaging_params.json"
fi

pyxis CFG=$CONFIG azishe
