# This script divides geant4 input files that have been split based on energy further down into chucks manageable by one node when simulating in the geant4 module. The number of particles per subfile will be determined by the energy range in which the particles fall.
# The script expects two arguments, the first one is the full path to the directory containing the splitted files based on energy, the second argument the full path to the directory to store the job input files. Make sure the energy splitted directory does not contain any other .txt files.

import sys
import glob
import numpy as np

# Reading the arguments
if(len(sys.argv) != 3):
    sys.exit("The script expects two arguments, the first one is the full path to the directory containing the splitted files based on energy, the second argument the full path to the directory to store the job input files. Make sure the directory containing the energy splitted directory does not contain any other .txt files.")
else:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

# A map telling how many particles can go in one file given the energy range, to keep simulation time for each job under about 3 hours
max_particles = {"below1.0E-02GeV":540000, "1.0E-02-1.0E-01GeV":360000, "1.0E-01-1.0E+00GeV":67500, "1.0E+00-1.0E+01GeV":9473, "1.0E+01-1.0E+02GeV":754, "1.0E+02-1.0E+03GeV":72, "1.0E+03-1.0E+04GeV":7, "1.0E+04-1.0E+05GeV":1, "above1.0E+05GeV":1}

# Getting all the input files
input_files = glob.glob(input_dir + "/*.txt")

# Looping over all the files
for input_file_name in input_files:

    # Getting an output file name base, assuming the input files end on .txt
    output_file_name_base = input_file_name.split("/")[-1][:-4]

    # Getting the energy range of the particles in the file
    energy_range = input_file_name.split("_")[-1][:-4]
    if(energy_range not in max_particles):
        sys.exit("Could not find the energy range of particles in %s" % input_file_name)

    # Reading the comment block in the beginning of the file
    input_file = open(input_file_name, 'r')
    comment_block = ''

    line = input_file.readline()

    while line and '#' in line:

        comment_block += line
        line = input_file.readline()
            
    input_file.close()

    # Reopening the file, reading and dividing it

    input_file = open(input_file_name, 'r')

    line = input_file.readline()
    counter = 0

    part = 1
    outputfile = open("%s/%s_part%s.txt" % (output_dir, output_file_name_base, part), 'w')
    outputfile.write(comment_block)

    while line:

        if(outputfile.closed):
            part += 1
            outputfile = open("%s/%s_part%s.txt" % (output_dir, output_file_name_base, part), 'w')
            outputfile.write(comment_block)
        
        if(line[0] != '#'): 
            outputfile.write(line)
            counter += 1

        if(counter == max_particles[energy_range]):
            outputfile.close()
            counter = 0

        line = input_file.readline()

    if(not outputfile.closed):
        outputfile.close()
