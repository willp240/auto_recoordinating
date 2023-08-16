#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../QuadSpeed/
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed/
python AnalyseData.py -i ${material} -f ${input_files} -s ${plot_dir} --overwriteTable
