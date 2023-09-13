import os

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

