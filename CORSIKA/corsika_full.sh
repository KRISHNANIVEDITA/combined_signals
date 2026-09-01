#!/bin/bash

# --- User-defined variables ---
zens=(0)                  # Zenith angles
azs=(0)                    # Azimuth angles
iters=(1 2 3)              # Iterations (if needed later)
energy=(1000000000)         # Energy
base_dir="/path to where to you want to store input file and reas file for sims/"

template_file="$base_dir/[name]/RUN000001.inp"   # Template RUN.inp
reas_template="$base_dir/[name]/SIM000001.reas"  # Template REAS file

storage_dir="//path to where to you want to store outputs/"

# --- Initialize RUNNR ---
runnr=1

# --- Loop over azimuths (and zenith if multiple) ---
for zen in "${zens[@]}"; do
    for i in "${!azs[@]}"; do
        az="${azs[$i]}"

        echo "Zenith: $zen, Azimuth: $az, RUNNR: $runnr"

        # Directory names
        sim_dir="c6e18.0z${zen}a${az}"
        local_dir="$base_dir$sim_dir"
        store_dir="$storage_dir/$sim_dir"

        # Create directories if they don't exist
        mkdir -p "$local_dir"
        mkdir -p "$store_dir"

        # Copy templates
        cp "$template_file" "$local_dir/RUN000001.inp"
        cp "$reas_template" "$local_dir/SIM000001.reas"

        # Modify RUN.inp using sed
        sed -i "s/^RUNNR .*/RUNNR $runnr/" "$local_dir/RUN000001.inp"
        sed -i "s/^ERANGE .*/ERANGE ${energy[0]} ${energy[0]}/" "$local_dir/RUN000001.inp"
        sed -i "s/^MAGNET .*/MAGNET 8.46 54.14/" "$local_dir/RUN000001.inp"
        sed -i "s/^THETAP .*/THETAP $zen $zen/" "$local_dir/RUN000001.inp"
        sed -i "s/^PHIP .*/PHIP $az $az/" "$local_dir/RUN000001.inp"

        # Increment RUNNR
        ((runnr++))
    done
done

echo "All RUN.inp files created successfully."
