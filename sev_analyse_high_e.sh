#!/usr/bin/sh
source /home/parkerw/Software/env-dev_5.34.38.sh
source /home/parkerw/Software/rat_master//env.sh
#cd /home/parkerw/Software/auto_recoordinating//../ScintEffectiveSpeed/ ## TODO fix this
cd /home/parkerw/Software/rat-tools_fork/FitCoordination/ScintEffectiveSpeed/
sleep $((1 + $RANDOM % 10))
python AnalyseData.py -s labppo_2p2_scintillator -i /data/snoplus3/parkerw/ratSimulations/Aug30_testdag//sev_recon_Round557/ -p /data/snoplus3/parkerw/ratSimulations/Aug30_testdag//plots -e interpolate -q /data/snoplus3/parkerw/ratSimulations/Aug30_testdag//sev_recon_HighE/ --overwriteTable
cd /home/parkerw/Software/auto_recoordinating/
python -c 'import db_utilities; db_utilities.write_current_sev( "labppo_2p2_scintillator", "/data/snoplus3/parkerw/ratSimulations/Aug30_testdag/")'
