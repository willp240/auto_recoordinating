#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../MultiPDFFull/
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/MultiPDFFull/ ## TODO fix this
python AnalyseData.py -s ${material} -i ${input_files} -n ${input_basename} -p ${plot_dir} -w
