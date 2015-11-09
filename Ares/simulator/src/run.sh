#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="meqtrees_sim_params.json"
fi

pyxis azishe -f
