#!/usr/bin/sh

source ${env_file}
sleep ${sleep}
cd ${submission_dir}/"../rat-tools_fork/FitPerformance/"

python fit_performance_tool.py ${input_files} ${coord} -f positionTimeFit -o ${output_file} -c plotting_1D.cfg --autoview  --debug
