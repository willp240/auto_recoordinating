import string
import sys
import os
import utilities
## import quad recoord tools also (and utils or w/e)

def setup_recon_jobs(job_name, out_dir, material, rat_root, env_file, fixed_energy, energy):

    ## make simulation use template macros inside rat-tools, not here
    ## also make inroot Quad template macros
    ## first run these macros over some simulation (with diff vels)
    ## edit quad analyse data so can input data file/path

    ## now run analyse data funcs over these files
    ## edit analyse data to have option to overwrite table (I guess will need to give it rat root)
    ## also edit analyse data to have plot made automatically and saved