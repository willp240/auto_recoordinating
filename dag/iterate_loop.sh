#!/usr/bin/sh

source ${env_file}
source ${rat_root}/env.sh

echo "entering python script" >> /home/parkerw/Software/auto_recoordinating/test.txt

#python test.py 2> /home/parkerw/Software/auto_recoordinating/test.err
#python 2> /home/parkerw/Software/auto_recoordinating/test.txt

python ${sub_dir}/template_loop.py -e ${env_file} -s ${sub_dir} -r ${rat_root} -m ${material} ${out_dir} 2> /home/parkerw/Software/auto_recoordinating/test.err

echo "done python script" >> /home/parkerw/Software/auto_recoordinating/test.txt

${bash_command}
then
    echo "exit 1"
    exit 1
else
    echo "EXIT 0"
    exit 0
fi