#!/usr/bin/sh
source /home/parkerw/Software/env-dev_5.34.38.sh
source /home/parkerw/Software/rat_master/env.sh
sleep $[($RANDOM%2)+1]s
rat /home/parkerw/Software/auto_recoordinating/dagman_tests/test1.mac
