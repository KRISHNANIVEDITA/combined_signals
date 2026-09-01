# This script makes the dagfile for submitting geant4 jobs to the cluster,
# using the reas and list files from CoREAS to set up the antenna array.
# It expects nine arguments, the first one is the input directory containing all the input files, the second one is the output directory to write the root files to, the third one is the log name. The fourth one is the output dir to write the dagfiles to. The fifth one is the zenith angle of the shower in degrees. The sixth one is the azimuth angle of the shower in degrees. The seventh one is the reas file. The eigth one is the list file. The ninth one is the atmosphere data file.

import glob
import sys
import os

import numpy as np
import time

np.random.seed(int(time.time()))

if(len(sys.argv) != 10):
    sys.exit("This script expects nine arguments, the first one is the input directory containing all the input files, the second one is the output directory to write the root files to, the third one is the log name base. The fourth one is the output dir to write the dagfiles to. The fifth one is the zenith angle of the shower (degrees). The sixth one is the azimuth angle of the shower (degrees). The seventh one is the reas file. The eighth one is the list file. The ninth is the atmosphere data file.")

else:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    log_name_base = sys.argv[3]
    dag_output_dir = sys.argv[4]
    zenith = float(sys.argv[5])
    azimuth = float(sys.argv[6])
    reas_fn = sys.argv[7]
    list_fn = sys.argv[8]
    atmos_fn = sys.argv[9]
    os.system("mkdir -p %s" % output_dir)
    os.system("mkdir -p %s" % dag_output_dir)

submit_file = '/user/knivedita/airtoice/submit_scripts/G5e18.0z40a0.submit'

input_dir_split = input_dir.split('/')
dag_file_name = ""
for elt in input_dir_split:
    if "GeV" in elt or "degr" in elt:
        dag_file_name += ("_%s" % elt)
dag_file = "%s/G5e18.0z40a0%s.dag" % (dag_output_dir, dag_file_name) # The dagfile to be created

# Getting all the input files from the input dir
input_files = glob.glob("%s/geant4*.txt" % input_dir)
input_files = [elt.split('/')[-1] for elt in input_files]

# Writing the dag file
dag = open(dag_file, 'w')
for i in range(len(input_files)):
    rand_int = int(np.random.rand()*215)
    output_file = input_files[i][:-4]
    dag.write('JOB job_%s %s\n' % (i, submit_file))
    dag.write('VARS job_%s INPUT_FILE="%s/%s" OUTPUT_FILE="%s/%s" RAND_INT="%i" ZENITH_ANGLE="%s" AZIMUTH_ANGLE="%s" REAS_FILE="%s" LIST_FILE="%s" ATMOS_FILE="%s" LOG_NAME="%s"\n' % (i, input_dir, input_files[i], output_dir, output_file, rand_int, zenith, azimuth, reas_fn, list_fn, atmos_fn, log_name_base + '_' + output_file))
print(dag_file)
dag.close()

#python make_dagfile.py /pnfs/iihe/radar/store/user/knivedita/ice_shelf/job_in/c0e16.0z45a180 /pnfs/iihe/radar/store/user/knivedita/ice_shelf/job_out/c0e16.0z45a180 1 /user/knivedita/airtoice/magfiles/ 45.0 180.0 /pnfs/iihe/radar/store/user/knivedita/ice_shelf/corsika_events/c0e16.0z45a180/SIM000001.reas /pnfs/iihe/radar/store/user/knivedita/ice_shelf/corsika_events/c0e16.0z45a180/SIM000001.list /user/knivedita/atm_summer.dat c0e16.0z45a180

#python make_dagfile.py /pnfs/iihe/radar/store/user/knivedita/ice_shelf/job_in/c1e16.0z45a315 /pnfs/iihe/radar/store/user/knivedita/ice_shelf/job_out/c1e16.0z45a315 1 /user/knivedita/airtoice/magfiles/ 45.0 315.0 /pnfs/iihe/radar/store/user/knivedita/ice_shelf/corsika_events/c1e16.0z45a315/SIM000002.reas /pnfs/iihe/radar/store/user/knivedita/ice_shelf/corsika_events/c1e16.0z45a315/SIM000002.list /user/knivedita/airtoice/make_corsika/atm_summer.dat c1e16.0z45a315
