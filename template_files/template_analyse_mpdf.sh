#!/usr/bin/sh

################################################################
### Template bash script to run mpdf analysis jobs on a cluster
### Options are written in by the scripts in job_sub
################################################################

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../MultiPDFFull/
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/MultiPDFFull/ ## TODO fix this
python AnalyseData.py -s ${material} -i ${input_files} -n ${input_basename} -p ${plot_dir} -w
