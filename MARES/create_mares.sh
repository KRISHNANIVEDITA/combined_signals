#!/bin/bash
# Source to your python environment
source /path/to/jupyter_env/bin/activate
name=${1}
listfile=${2}
coreas_dir=${3}
energy=${4}
zenith=${5}
azimuth=${6}
core_coreas=${7}
output_dir=${8}

python3 create_mares.py \
    "$name" \
    "$listfile" \
    "$coreas_dir" \
    "$energy" \
    "$zenith" \
    "$azimuth" \
    "$core_coreas" \
    "$output_dir"
