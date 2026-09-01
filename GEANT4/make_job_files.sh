#!/bin/bash

# The path to the corsikaread_thin (or corsikaread, in case of no thinning)  executable
corsikaread_thin=/user/knivedita/airtoice/python_scripts/corsikaread_thin

# The maximum radius of the footprint for which the particles will be read out, in cm
# This is defined in the plane perpendicular to the shower axis frame,
# i.e. the footprint will be an ellipse of 
# width upper_radius/cos(zenith) and an height of upper_radius, aligned with the 
# azimuth angle
upper_radius=100

#ROOTSYS="/cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_7_x86_64/i3ports/root-v5.34.18"
#eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`

source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_104 x86_64-el9-gcc13-opt

input_file=${1}
output_dir=${2}
zenith=${3}
azimuth=${4}
corsika_log_file=${5}
echo "Using TMPDIR: ${TMPDIR}"
# Coppying the file
cp ${input_file} ${TMPDIR}/corsika_file


# Using corsikaread to read the file
echo "${TMPDIR}/corsika_file                                                                      " > ${TMPDIR}/corsikaread_input
cd ${TMPDIR}/

${corsikaread_thin} < ${TMPDIR}/corsikaread_input > ${TMPDIR}/corsikaread_output
rm ${TMPDIR}/corsika_file
rm ${TMPDIR}/corsikaread_input
rm ${TMPDIR}/corsikaread_output

#cp ${TMPDIR}/corsika_file ${output_dir}
#cp ${TMPDIR}/corsikaread_input ${output_dir}
#cp ${TMPDIR}/corsikaread_output ${output_dir}

# Making the geant4 input file using the fort.8 file
python /user/knivedita/airtoice/python_scripts/make_geant4_input_file_azimuth_rot.py ${TMPDIR}/fort.8 ${TMPDIR} 0 ${upper_radius} ${zenith} ${azimuth} ${corsika_log_file}
rm ${TMPDIR}/fort.8
#rm ${TMPDIR}/id_histo_file.root

# Splitting the geant4 input file in energy
mkdir ${TMPDIR}/energy_splitted/
python /user/knivedita/airtoice/python_scripts/split_on_energy_geant4_input_file.py ${TMPDIR}/geant4_input_file.txt ${TMPDIR}/energy_splitted/
rm ${TMPDIR}/geant4_input_file.txt

# Splitting the files further down into job files
mkdir ${TMPDIR}/jobs_input/
python /user/knivedita/airtoice/python_scripts/split_in_job_files_geant4_input_file.py ${TMPDIR}/energy_splitted/ ${TMPDIR}/jobs_input/
rm -r ${TMPDIR}/energy_splitted/

cp -f ${TMPDIR}/jobs_input/* ${output_dir}
rm -r ${TMPDIR}/jobs_input/