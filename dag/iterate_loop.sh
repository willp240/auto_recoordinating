#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh

python ${sub_dir}/template_loop.py -e ${env_file} -s ${sub_dir} -r ${rat_root} -m ${material} ${out_dir}

${bash_command}
then
    exit 1
else
    ## Check how many runs it took to converge, and update the sh file
    filename="${out_dir}/sev_values.txt"
    sev_string=${sev_string_command} 
    sev_array=${sev_array_command}
    round_num=${round_num_command}

    sh_file_string=${sh_file_string_command}
    sub_str="Round"

    ${sed_command} "${out_dir}/sev_analyse_high_e/sh/sev_analyse_high_e.sh"

    exit 0
fi
