#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../QuadSpeed/
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed/
python AnalyseData.py -s ${material} -i ${input_files} -p ${plot_dir} --overwriteTable
