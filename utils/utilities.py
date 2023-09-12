import os

## Speeds to run over are taken from
## See README for details on why these are re-hardcoded here
SEVSpeeds  = [182.0, 182.5, 183.0, 183.5, 184.0, 184.5, 185.0, 185.5, 186.0, 186.5, 187.0, 187.5]
QuadSpeeds = [175.0, 180.0, 185.0, 190.0, 195.0, 200.0, 205.0]

## Parameters you can tweak to optimise speed of recoordination
sev_files_per_velocity = 5
quad_files_per_velocity = 1
sim_num_files = 200
num_evs_per_file = 500
convergence_criteria = 0.05

### Check if directory exists, create it if it doesn't
def check_dir(dname):

    if(dname[-1] != "/"):
        dname = dname + "/"
    direc = os.path.dirname(dname)
    try:
        os.stat(direc)
    except:
        os.makedirs(direc)
        print ("Made directory %s...." % dname)
    return dname

