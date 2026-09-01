import re
import os 
import numpy as np

import glob
import subprocess
import matplotlib.pyplot as plt
import math
import subprocess
import random
import pandas as pd
import sys
import shutil
from matplotlib.lines import Line2D
def mares_to_CoREAS_Etrans(xM, yM, zM,phi):
    phi=np.radians(phi)
    #xC = xM*np.cos(phi) + yM*np.sin(phi)
    xC=-yM
    #yC = xM*np.sin(phi) - xM*np.cos(phi)
    yC=xM
    zC = zM
    return np.column_stack((xC, yC, zC))
def natural_sort_key(path):
    return int(re.search(r'antenna(\d+)\.dat', path).group(1))
def load_grid(listfile, coreas_dir,list_base,coreas_base):
        """
        Read one list file and return list of entries. 
        You might want to change this depending on your antenna names. Here the form is $"name_{antennaindex}"$
        """
        
        entries_local = []
        print(listfile, coreas_dir,list_base,coreas_base)
        with open(listfile, "r") as f:

            for line in f:
                
                line = line.strip()
                if not line.startswith("AntennaPosition"):
                    continue

                toks = line.split()
                if len(toks) < 6:
                    continue
                
                try:
                    x_cm = float(toks[2])
                    y_cm = float(toks[3])
                    z_cm = float(toks[4])
                    label = toks[5]
                    m = re.fullmatch(re.escape(list_base) + r"(\d+)", label)
                    if not m:
                        continue
                    p = int(m.group(1))

                    # convert cm → m
                    x_m = x_cm / 100.0
                    y_m = y_cm / 100.0
                    z_m = z_cm / 100.0

                    if coreas_dir is None or coreas_base is None:
                        file = ""
                    else:
                        file = f"{coreas_dir}/{coreas_base}{p}.dat"
                    entries_local.append((p, x_m, y_m, z_m, file))
                except Exception:
                    continue
        return entries_local

def change_all(reference_file,new_file, run_name, path_out,core, x_r, y_r, z_r, zen, az, energy):
    src = "/user/knivedita/MARES/build/RETCR2024_1rx.cfg"
    #src=reference_file
    print(reference_file,new_file, run_name, path_out,core, x_r, y_r, z_r, zen, az, energy)
    shutil.copy2(src, new_file)
    with open(new_file, "r") as f:
        
        lines = f.readlines()
    # NEW cascade values
    new_zen = 180.0 - zen
    new_az = 90.0 + az
    # States
    in_cs0 = False
    in_cs0_pos = False
    in_cs0_dir = False
    in_rx0 = False
    in_rx0_pos = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # ======================================================
        #                 RUN NAME & OUTPUT PATH
        # ======================================================
        if stripped.startswith("name ="):
            lines[i] = f'name = "{run_name}";\n'
            continue

        if stripped.startswith("path_out"):
            lines[i] = f'path_out="{path_out}";\n'
            continue
        # ======================================================
        #                 CASCADE CS0 BLOCK
        # ======================================================
        if stripped.startswith("{   #--- CS0 ---#"):
            in_cs0 = True
            continue
        if in_cs0:
            if stripped.startswith("position = {"):
                in_cs0_pos = True
                continue
            if in_cs0_pos:
                if stripped.startswith("x ="):
                    lines[i] = f"        x = {core[0]};\n"
                elif stripped.startswith("y ="):
                    lines[i] = f"        y = {core[1]};\n"
                elif stripped.startswith("z ="):
                    lines[i] = f"        z = {0.0};\n"
                elif stripped.startswith("};"):
                    in_cs0_pos = False
            # ---- direction block ----
            if stripped.startswith("direction = {"):
                in_cs0_dir = True
                continue
            if in_cs0_dir:
                if stripped.startswith("zenith"):
                    lines[i] = f"        zenith  = {new_zen};\n"
                elif stripped.startswith("azimuth"):
                    lines[i] = f"        azimuth = {new_az};\n"
                elif stripped == "};":
                    in_cs0_dir = False

            # ---- energy ----
            if stripped.startswith("energy"):
                lines[i] = f"    energy = {energy};\n"
            # end CS0 block
            if stripped.startswith("},"):
                in_cs0 = False
                continue
        # ======================================================
        #                    RECEIVER RX0 BLOCK
        # ======================================================
        if stripped.startswith("{#--- RX0 ---#"):
            in_rx0 = True
            continue

        if in_rx0:
            # ---- position block ----
            if stripped.startswith("position = {"):
                in_rx0_pos = True
                continue

            if in_rx0_pos:
                if stripped.startswith("x ="):
                    lines[i] = f"        x = {x_r};\n"
                elif stripped.startswith("y ="):
                    lines[i] = f"        y = {y_r};\n"
                elif stripped.startswith("z ="):
                    lines[i] = f"        z = {z_r};\n"
                elif stripped == "};":
                    in_rx0_pos = False

            # end RX0 block
            if stripped.startswith("},"):
                in_rx0 = False
                continue

    # ======================================================
    #                WRITE UPDATED FILE
    # ======================================================
    with open(new_file, "w") as f:
        f.writelines(lines)
    print("✓ Updated CS0 (zenith, azimuth, energy) and RX0 (x,y,z).")

    
def runMARES(name,listfile,list_base,reference_file,new_config_file,output_dir,core_coreas,energy,zenith,azimuth,coreas_dir,coreas_base):
    entries = []
    print(core_coreas)
    core_radar = -core_coreas[1],core_coreas[0]
    
    entries_1 = load_grid(listfile, coreas_dir,list_base,coreas_base)
    entries = entries_1 
    #print('entries are',entries)
    
    x_pos_m = np.array([x for (_, x, _, _,_) in entries])
    y_pos_m = np.array([y for (_, _, y, _, _) in entries])
    z_pos_m = np.array([z for (_, _, _, z, _) in entries])
    files =   np.array([f for (_, _, _, _,f) in entries])
    ice_alt = 3200.0
    p_list = np.array([p for (p, _, _, _, _) in entries])
    #print(entries)
    ant_idx = np.arange(len(entries))
    # build mask
    mask = ~((x_pos_m == -100.0) & (y_pos_m == 0.0))

    # apply mask
    ant_idx = ant_idx[mask]
    ant_idx=ant_idx[:2]
    print(ant_idx)
    plt.figure()
    
    for id in ant_idx:
        run_name=f'{name}_{id}'
        x_r,y_r,z_r = -y_pos_m[id] + core_radar[0],x_pos_m[id] + core_radar[1], z_pos_m[id] - ice_alt
        change_all(
            reference_file,new_config_file,run_name, output_dir,
            core_radar,
            x_r,
            y_r,
            z_r,
            zenith, azimuth, energy
        )

        subprocess.run(
            ["/user/knivedita/MARES/build/MARES", new_config_file]
        )
    
    '''
    entries = np.array(entries, dtype=object)
    entries_valid = entries[ant_idx]
    # keep only x, y, z (indices 1, 2, 3)
    xyz = entries_valid[:, 1:3]
    DF = pd.DataFrame(xyz, columns=['x', 'y'])
    ant1_files = sorted(
        glob.glob('/user/knivedita/airtoice/results/RET/G4z20_IRT/1/antenna*.dat'),
        key=natural_sort_key
    ) 
    '''


if len(sys.argv) != 9:
    sys.exit(
        "Usage: create_MARES.py "
        "<name> <listfile> <coreas_dir> "
        "<energy> <zenith> <azimuth> <core_coreas> <output_dir>"
    )

name = sys.argv[1]
listfile = sys.argv[2]
coreas_dir = sys.argv[3]
energy = float(sys.argv[4])
zenith = float(sys.argv[5])
azimuth = float(sys.argv[6])
# core_coreas passed as "x,y"
core_coreas = np.array([float(x) for x in sys.argv[7].split(",")])
output_dir = sys.argv[8]



    
#name = "G4e17.0z0a0"
## get listfile and the base name of the antennas (if you have) in the SIM.list file
#listfile  = f"/pnfs/iihe/radar/store/user/knivedita/RET/airshowers/{name}/1/SIM000001.list"
with open(listfile, "r") as f:
    first_line = f.readline()
token = first_line.split()[-1]
list_base = re.sub(r'\d+$', '', token)

## get coreas antenna directory and the base name of the antennafiles (if you have) in the folder
#coreas_dir = f"/pnfs/iihe/radar/store/user/knivedita/RET/airshowers/{name}/1/SIM000001_coreas/" 
bases = set()
for fname in os.listdir(coreas_dir):
    if fname.endswith(".dat"):
        base = re.sub(r'\d+\.dat$', '', fname)
        bases.add(base)
for b in sorted(bases):
    coreas_base = b
    print(coreas_base)

#energy=25.0
#zenith=0
#azimuth=0
#core_coreas=np.array([10.0,0.0])
#output_dir = '/user/knivedita/MARES/results/ex/'

reference_file = f"/user/knivedita/MARES/build/{name}.cfg"
new_config_file = f"/user/knivedita/MARES/build/{name}_scratch.cfg"
runMARES(name,listfile,list_base,reference_file,new_config_file,output_dir,core_coreas,energy,zenith,azimuth,coreas_dir,coreas_base)
    