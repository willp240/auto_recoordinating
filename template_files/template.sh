#!/usr/bin/sh

######################################################
### Template bash script to run rat jobs on a cluster
### Options are written in by the scripts in job_sub
######################################################

source ${env_file}
cd ${rat_root}
source ${rat_root}/env.sh
sleep ${sleep}
rat ${macro_name}
