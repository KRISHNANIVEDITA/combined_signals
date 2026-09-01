# This script divides a geant4 input file into different files based on energy: the particles with an
# energy between E_underlim and E_underlim*10 go in the first file, the particles with an energy between
# E_underlim*10 and E_underlim*100 go in the second file, ..., the particles with an energy between 
# E_uplim/10 and E_uplim go in the last file.
# TIP: use cat * | grep -v '#' | wc -l to count lines of (a) files ignoring the lines with '#'

# It takes two arguments, the first one being the full path to the input file that you want to divide, the second one the full path to the directory to write the output files to.

import sys
import numpy as np

import importlib
mass_file = importlib.import_module("particle_masses")

########################################################################
############### PARAMETERS THAT YOU MIGHT WANT TO CHANGE ###############
########################################################################

E_underlim = 1.e-2 # The under limit of the energy in GeV
E_uplim = 1.e5 # The upper limit of the energy in GeV

########################################################################
########################################################################
########################################################################

# Reading the arguments
if(len(sys.argv) != 3):
    sys.exit("This script takes two arguments, the first one being the full path to the input file that you want to divide, the second one the full path to the directory to write the output files to.")
else:
    input_file_name = sys.argv[1]
    output_dir = sys.argv[2]

# Making an output file name base, assuming the input file name ends in ".txt"
output_file_name_base = output_dir + input_file_name.split("/")[-1][:-4]

# The particle ids and masses in GeV/c**2 of the particles. 
particle_masses = mass_file.get_particle_masses()

# Will tell us what units the input file is using

energy_unit_str = "NONE"
length_unit_str = "NONE"

inputfile = open(input_file_name, 'r')

# Searching the units

line = inputfile.readline()[:-1] # Dropping the last character of the line, which is \n.

while line:
    if("Units are:" in line):
        split_line = line.split(' ')
        energy_unit_str = split_line[3]
        length_unit_str = split_line[4] # Need to remove the \n character following the length unit
        break
    line = inputfile.readline()[:-1]

print("Found the units. Energy is in %s and length in %s." % (energy_unit_str, length_unit_str))
inputfile.close()

# Setting the units

energy_unit = -99. # Will contain the unit of energy in MeV.
length_unit = -99. # Will contain the unit of length in cm.

if(energy_unit_str == "MeV"):
    energy_unit = 1.
elif(energy_unit_str == "GeV"):
    energy_unit = 1.e3
else:
    sys.exit("The unit of energy is %s. This is not yet implemented..." % energy_unit_str)

if(length_unit_str == "cm"):
    length_unit = 1.
elif(length_unit_str == "m"):
    length_unit = 100.
else:
    sys.exit("The unit of length is %s. This is not yet implemented..." % length_unit_str)

# Making the output files
outputfiles = []
i = 0
while(E_underlim * 10**i < E_uplim):
    outputfiles.append(open(output_file_name_base + "_%s-%sGeV.txt" % ('%.1E' % (E_underlim*10.**i), '%.1E' % (E_underlim*10.**(i+1))), 'w'))
    i += 1
outputfiles.append(open(output_file_name_base + "_below%sGeV.txt" % ('%.1E' % E_underlim), 'w'))
outputfiles.append(open(output_file_name_base + "_above%sGeV.txt" % ('%.1E' % E_uplim), 'w'))

# Reading and sorting out the file. Writing the lines which match the energy conditions to new file.

inputfile = open(input_file_name, 'r')
line = inputfile.readline()[:-1]

while line:

    if(line[0] != '#'):

        line_split = line.split(' ')

        # The particle id
        part_id = int(line_split[0])

        if(part_id not in particle_masses):
            sys.exit("Found a particle id which is not implemented. Part id: %s" % part_id)

        # Reading the momenta and converting to internal units (MeV/c)
        px = float(line_split[1])*float(energy_unit)
        py = float(line_split[2])*float(energy_unit)
        pz = float(line_split[3])*float(energy_unit)

        # The total momentum in MeV/c
        p = np.sqrt(px*px + py*py + pz*pz)

        # The energy in MeV
        m = particle_masses[part_id]*1000 # Changing to MeV/c^2
        E = np.sqrt(p*p + m*m)

        i = 0
        found_right_file = False
        while(i < (len(outputfiles) - 2) and not found_right_file):
            if(E >= (E_underlim*10.**i)*1000. and E < (E_underlim*10.**(i+1))*1000.):
                outputfiles[i].write(line + '\n')
                found_right_file = True
            i += 1
        if(not found_right_file):
            if(E < E_underlim*1000.):
                outputfiles[-2].write(line + '\n')
            elif(E >= E_uplim*1000.):
                outputfiles[-1].write(line + '\n')
            else:
                sys.exit("Cannot find right file for line %s." % line)
            
    else:
        for outputfile in outputfiles:        
            outputfile.write(line + '\n')

    line = inputfile.readline()[:-1]

inputfile.close()
for outputfile in outputfiles:
    outputfile.close()
