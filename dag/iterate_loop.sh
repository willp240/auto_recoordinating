#!/usr/bin/sh 

###################################################################
### Script run at the end of each iteration of the mpdf-sev loop
### It calls a python script to determine if we've converged
### If it hasn't converged, overwrite submission scripts and dag
### splice and exit with 1, triggering a rerunning of the loop
### Options are written in by loop.py in job_sub
###################################################################

source ${env_file}
source ${rat_root}/env.sh

cd ${sub_dir}

python ${sub_dir}/job_sub/iterate_loop.py -e ${env_file} -s ${sub_dir} -r ${rat_root} -m ${material} ${out_dir}

## This command gets written by the loop script in job_sub
## It checks the output of the previous python script (did it exit 1 or 0)
${bash_command}
then
    ## If iterate_loop hadn't finished converging return 1 to trigger rerunning the loop
    exit 1
else
    ## If we did converge, check how many runs it took to converge, and update the bash file with a new round num
    filename="${out_dir}/sev_values.txt"
    sev_string=${sev_string_command} 
    sev_array=${sev_array_command}
    round_num=${round_num_command}

    sh_file_string=${sh_file_string_command}
    sub_str="round"

    ${sed_command} "${out_dir}/sev_analyse_high_e/sh/sev_analyse_high_e.sh"

    ## Exit 0 so the loop is not retried any more times
    exit 0
fi
