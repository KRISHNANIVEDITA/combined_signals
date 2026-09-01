# This script reads a corsika output file and makes an input file for the geant4 application.
# This version uses the same t = 0 point as CoREAS, using the time of entry in the atmosphere stated in
# the Corsika output log.

import numpy as np
#import ROOT
import sys

import importlib
script_file = importlib.import_module("read_corsika_fortran_file")

########################################################################
############### PARAMETERS THAT YOU MIGHT WANT TO CHANGE ###############
########################################################################

length_unit = 1. # The unit of length in cm
length_unit_str = "cm" # The unit of length in string format
energy_unit = 1. # The unit of energy in GeV. Unit of momentum is (unit of energy)/c.
energy_unit_str = "GeV" # The unit of energy in string format. Unit of momentum is (unit of energy)/c.
time_unit = 1. # The unit of time in ns
time_unit_str = "ns" # The unit of time in string format

depth_active_volume = 2000. # The depth of the active volume in cm

########################################################################
########################################################################
########################################################################

# Reading the filename
if(len(sys.argv) != 8):
    sys.exit("This script expects 7 arguments, the first argument is the full path to the corsika output file, the second argument is the full path to the directory write the output file to, the third argument is the radius under limit in cm, the fourth argument is the radius upper limit in cm, the fifth argument is the zenith angle of the shower in degrees, the sixth argument is the azimuth angle of the shower in degrees, the zeventh argument is the output log file from the corsika simulation.")
else:
    input_file_name= sys.argv[1]
    output_file_dir = sys.argv[2]
    radius_underlim = float(sys.argv[3])
    radius_upperlim = float(sys.argv[4])
    zenith = float(sys.argv[5])*np.pi/180.
    azimuth = float(sys.argv[6])*np.pi/180.
    output_log_fn = sys.argv[7]

# This function checks if a given x,y pair lies within an ellipse with width 2a and height 2b:
def in_ellipse(x, y, a, b):
    if(a == 0 or b == 0): # No ellipse...
        return False
    elif(x**2/a**2 + y**2/b**2 < 1):
        return True
    else:
        return False

# Reading the fortran output file
# We want to have an elliptical footprint on the ice based on the zenith angle, so as a starter 
# we'll read out the particles that are located in the circle containing the ellipse.
a_upper = radius_upperlim/np.cos(zenith)
b_upper = radius_upperlim
a_under = radius_underlim/np.cos(zenith)
b_under = radius_underlim
z_first_interaction, saved_particle_data = script_file.read_corsika_fortran_file(input_file_name, b_under, a_upper)
for i in range(len(z_first_interaction)):
    if(z_first_interaction[i] >= 0):
        sys.exit("The z coordinate of first interaction point of event %s is not negative, which indicates TSTART = false. Aborting..." % i)

print("Read the Corsika fortran output file. Now creating the geant4 input file.")

# Opening a file for the id histogram, creating the histogram
#histo_file = ROOT.TFile(output_file_dir + "/id_histo_file.root", "RECREATE")
#id_histo = ROOT.TH1D("id_histo", "Histogram giving the weighted number of id's", 195, 0.5, 195.5)

# Creating an output file
output_file = open(output_file_dir + "/geant4_input_file.txt", 'w')

# Calculating the number of particle entries
npe = 0.
for ev in range(len(saved_particle_data)):
    npe += len(saved_particle_data[ev])

# CoREAS defines t = 0 at the time when the primary particle would have hit the shower core
# (i.e. the core of the footprint) if it would not have had any interactions in the air.
# Corsika defines t = 0 at the top of the atmosphere when TSTART parameter in the
# steering file = T, which is by default when you use CHERENKOV (and thus CoREAS)
# Here we will assume Corsika defined t = 0 at the top of the atmosphere, and will shift to the 
# CoREAS time frame

print("ASSUMING CORSIKA USES t = 0 AT THE TOP OF THE ATMOSPHERE (I.E. TSTART WAS SET TO TRUE, WHICH IS BY DEFAULT IF YOU ARE USING CONEX, CURVED, SLANT, STACKIN, CERENKOV OR IACT)")

c0 = 299792458e-7 # Speed of light in vacuum, in cm/ns
height_entrance = -999.9e2 # The height of the entrance of the primary particle in the atmosphere,
                           # wrt sea level
part_readout_lvl = -999.9e2 # The height of the particle readout level in the corsika simulation

output_log_file = open(output_log_fn, 'r')
line = output_log_file.readline()
while(line):
    if("STARTING ALTITUDE AT" in line):
        line = line.split(" ")
        height_entrance = float(line[8])
    if("OBSERVATION LEVEL # IN  CM    AND IN   G/CM**2" in line):
        line = output_log_file.readline() # Advancing to the next line
        line = line.split(" ")
        part_readout_lvl = float(line[17])
        line = output_log_file.readline() # Making sure there's no second observation level
        line = line.split(" ")
        line = [elt for elt in line if len(elt) != 0]
        if(len(line) == 3 and line[0] == '2'):
            sys.exit("Looks like you were using multiple observation levels, which is not supported by CoREAS. You're using the make_geant4_input_file_azimuth_rot.py script designed to work with CoREAS, so something went wrong...")
        else:
            break # We can leave the while loop and close the file
    line = output_log_file.readline()
output_log_file.close()

h = height_entrance - part_readout_lvl # The height of t = 0 in Corsika in cm, wrt particle readout level
time_diff = h/(c0*np.cos(zenith)) # The time difference between t = 0 in Corsika and t = 0 in CoREAS
                                  # i.e. t_coreas = t_corsika - time_diff

# Writing down some information
output_file.write("#################################################################\n")
output_file.write("# Units are: %s %s %s\n" % (energy_unit_str, length_unit_str, time_unit_str))
output_file.write("# Number of particles in original file (not weighted): %s\n" % npe)
output_file.write("# Format: part_id px(%s) py(%s) pz(%s) x(%s) y(%s) z(%s) t(%s) weight\n" % (energy_unit_str, energy_unit_str, energy_unit_str, length_unit_str, length_unit_str, length_unit_str, time_unit_str))
output_file.write("# NOTE: using the geant4 axis system here, following the convention of CoREAS for t = 0\n")
output_file.write("#################################################################\n")

# Writing a line for every particle we found, over all events
for ev in range(len(saved_particle_data)):

    for particle in saved_particle_data[ev]:
        
        part_id = particle[0]
        px = particle[1]/float(energy_unit)
        py = particle[2]/float(energy_unit)
        pz = particle[3]/float(energy_unit)
        x = particle[4]/float(length_unit)
        y = particle[5]/float(length_unit)
        t = (particle[6]-time_diff)/float(time_unit)
        w = particle[7]

        z = (depth_active_volume*1./2.)/float(length_unit)

        # Rotating such that azimuth = 0
        # This means we rotate the x- and y-axis over an angle = azimuth
        xrot = x*np.cos(azimuth) + y*np.sin(azimuth)
        yrot = y*np.cos(azimuth) - x*np.sin(azimuth)
        x = xrot
        y = yrot

        pxrot = px*np.cos(azimuth) + py*np.sin(azimuth)
        pyrot = py*np.cos(azimuth) - px*np.sin(azimuth)
        px = pxrot
        py = pyrot

        # Checking if particle falls in the elliptical footprint
        if(not in_ellipse(x, y, a_under, b_under) and in_ellipse(x, y, a_upper, b_upper)):

            # The particle id
            output_file.write("%s " % part_id)
            # The momentum.
            # Corsika gives us the momenta in the x, y and -z (!) direction
            # according to its axis system
            # In the Geant4 axis system we use that means:
            # * px_G = px_C
            # * py_G = -pz_C
            # * pz_G = -py_C
            output_file.write("%s %s %s " % (px, -1*pz, -1*py))
            # The position.
            # Corsika gives us the x and y coordinates according to its axis system
            # In the Geant4 axis system we use that means:
            # * x_G = x_C
            # * y_G = z (see z variable above)
            # * z_G = -y_C
            output_file.write("%s %s %s " % (x, z, -1*y))
            # The arrival time.
            output_file.write("%s " % t)
            # The weight.
            output_file.write("%s\n" % w)

            #id_histo.Fill(part_id, w)

# Closing the output files
output_file.close()
#id_histo.Write()
#histo_file.Close()

print("Finished making the Geant4 input file.")
