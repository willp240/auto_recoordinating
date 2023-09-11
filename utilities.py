import os

SEVSpeeds  = [182.0, 182.5, 183.0, 183.5, 184.0, 184.5, 185.0, 185.5, 186.0, 186.5, 187.0, 187.5]
QuadSpeeds = [175.0, 180.0, 185.0, 190.0, 195.0, 200.0, 205.0 ]

sev_files_per_velocity = 10
quad_files_per_velocity = 1
sim_num_events = 200


def check_dir(dname):
    """Check if directory exists, create it if it doesn't"""
    if(dname[-1] != "/"):
        dname = dname + "/"
    direc = os.path.dirname(dname)
    try:
        os.stat(direc)
    except:
        os.makedirs(direc)
        print "Made directory %s...." % dname
    return dname

