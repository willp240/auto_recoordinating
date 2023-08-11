#!/usr/bin/sh

source ${env_file}
cd ${rat_root}
source ${rat_root}/env.sh
rat ${macro_name}
