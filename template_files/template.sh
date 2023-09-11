#!/usr/bin/sh

source ${env_file}
cd ${rat_root}
source ${rat_root}/env.sh
sleep ${sleep}
rat ${macro_name}
