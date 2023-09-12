#################################################################
### Template bash script to FitPerformanceTool jobs on a cluster
### Options are written in by the scripts in job_sub
#################################################################

#!/usr/bin/sh

source ${env_file}
sleep ${sleep}
cd ${submission_dir}/"../rat-tools_fork/FitPerformance/" ## TODO update this

python fit_performance_tool.py ${input_files} ${coord} -f positionTimeFit -o ${output_file} -c plotting_1D.cfg --autoview  --debug
