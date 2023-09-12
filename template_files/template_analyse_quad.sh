#!/usr/bin/sh

################################################################
### Template bash script to run quad analysis jobs on a cluster
### Options are written in by the scripts in job_sub
################################################################

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../QuadSpeed/
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed/ ## TODO: fix this
sleep ${sleep}
python AnalyseData.py -s ${material} -i ${input_files} -p ${plot_dir} -w
