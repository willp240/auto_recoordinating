import os
import rat
from ROOT import RAT

### Check in ratdb files if Scint Eff Vel has been recoordinated for this material before
def check_first_sev( material ):
    
    ## Load up all the relevant tables
    db = RAT.DB.Get()
    db.LoadAll(os.environ["GLG4DATA"], "*EFFECTIVE_VELOCITY*.ratdb")
    link = db.GetLink("EFFECTIVE_VELOCITY", material)
    ## If it's not been recoordinated before, we will use the default material initially
    ## So return defaultMaterial=True if we can't get a velocity from the table yet
    try:
        link.GetD("inner_av_velocity")
    except:
        defaultMaterial = True
    else:
        defaultMaterial = False

    return defaultMaterial

### Get current SEV value from ratdb table and write it to a text file
### This is needed because we want to be able to access previous velocities
### when determining if we have converged
def write_current_sev( material, out_dir ):
    
    ## Load up all the relevant tables
    db = RAT.DB.Get()
    db.LoadAll(os.environ["GLG4DATA"], "*EFFECTIVE_VELOCITY*.ratdb")
    db = RAT.DB.Get()
    link = db.GetLink("EFFECTIVE_VELOCITY", material)
    curr_val = link.GetD("inner_av_velocity")

    ## Write the latest velocity to the text file
    sev_filename = "{0}/sev_values.txt".format(out_dir)
    try:
        sev_file = open(sev_filename, 'r')
        sev_text = sev_file.read()
    except:
        sev_text = ""

    curr_val_string = str(curr_val) + "\n"
    sev_text += curr_val_string

    updated_file = open(sev_filename, 'w')
    updated_file.write(sev_text)
