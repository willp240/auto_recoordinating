#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh
#cd ${submission_dir}/../ScintEffectiveSpeed/  ## TODO fix this
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/ScintEffectiveSpeed/
sleep ${sleep}
python AnalyseData.py -s ${material} -i ${input_files} -p ${plot_dir} -e ${energy_choice} -q ${input_files_high}  -w 
cd ${sub_dir}
python -c 'import db_utilities; db_utilities.write_current_sev( "${material}", "${out_dir}")'
