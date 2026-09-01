#!/bin/bash

# Arguments are the corsika input file, the run number (XXXXXX), the atmosphere file, the reas file, the list file and the directory to store all the output files.

run_dir=/path/to/corsika-77500/run/

# Should be the name of the corsika executable in the run directory
corsika_exec=corsika_QGSJET

cp -r ${run_dir} ${TMPDIR}/run
cd ${TMPDIR}/run

# Needed for EPOS
cp -r ${run_dir}/../epos ${TMPDIR}/

input_file=corsika.inp
cp ${1} ${input_file}

run_number=${2}

atmos_file=Atmosphere.dat
cp ${3} ${atmos_file}

reas_file=SIM${run_number}.reas
cp ${4} ${reas_file}

list_file=SIM${run_number}.list
cp ${5} ${list_file}

output_file=RUN${run_number}.log

export LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH

./${corsika_exec} < corsika.inp > ${output_file}

cp -f RUN${run_number}* ${6}
cp -f DAT${run_number}* ${6}
cp -rf SIM${run_number}* ${6}

cd ${TMPDIR}
rm -rf run
