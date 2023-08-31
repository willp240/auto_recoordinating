import string
import sys
import os
import rat
from ROOT import RAT

def check_first_sev( material ):
    
    ## Check if scint eff vel has been recoordinated for this material before
    db = RAT.DB.Get()
    db.LoadAll(os.environ["GLG4DATA"], "*EFFECTIVE_VELOCITY*.ratdb")
    link = db.GetLink("EFFECTIVE_VELOCITY", material)
    try:
        link.GetD("inner_av_velocity")
    except:
        defaultMaterial = True
    else:
        defaultMaterial = False
    
    return defaultMaterial

def write_current_sev( material, out_dir ):
    
    ## Get newly recoordinated scint eff vel
    db = RAT.DB.Get()
    db.LoadAll(os.environ["GLG4DATA"], "*EFFECTIVE_VELOCITY*.ratdb")
    db = RAT.DB.Get()
    link = db.GetLink("EFFECTIVE_VELOCITY", material)
    curr_val = link.GetD("inner_av_velocity")

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
