#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="meqtrees_sim_params.json"
fi

cp /code/pyxis-*.py /code/tdlconf.profiles .
pyxis azishe -f
