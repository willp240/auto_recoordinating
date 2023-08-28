import sys
import os
import string
import argparse
import utilities
import loop
import rat
from ROOT import RAT

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Launch a load of identical rat simulation jobs")
    parser.add_argument('out_dir', type=str, help='directory to place reprocessed files')
    parser.add_argument('-e', '--env_file', type=str,
                        help='path to environment file',
                        default="/path/to/environment/env.sh")
    parser.add_argument("-s", "--submission_directory", type=str,
                       default="/path/to/this/repository/rat_submission/",
                       help="path to the directory this file is in, for outputs and inputs")
    parser.add_argument("-r", "--rat_root", type=str,
                       default="/path/to/rat/",
                       help="base rat directory from which the scripts will be run")
    parser.add_argument("-m", "--material", type=str,
                       default="labppo_2p2_scintillator",
                       help="which material are we recoordinating for?")
    parser.add_argument("-g", "--geo_file", type=str, 
                        default = "geo/snoplusnative.geo",
                        help = "Geometry File to use - location relative to rat/data/")
    parser.add_argument("-x", "--extraAVShift", type=str, 
                        default = "",
                        help = "Set z coordinate of AV centre. Overwrites shift set in geo file")
    args = parser.parse_args()

    ## check if output and condor directories exist, create if they don't
    out_dir = utilities.check_dir(args.out_dir)
    dag_dir = utilities.check_dir("{0}/dag/".format(out_dir))
    plot_dir = utilities.check_dir("{0}/plots/".format(out_dir))

    material = args.material
    rat_root = args.rat_root
    env_file = args.env_file
    submission_dir = args.submission_directory
    geo_file = args.geo_file
    if args.extraAVShift:
        avShift = "/rat/db/set GEO[av] position [0.,0.," + args.extraAVShift + "]"
    ## Check if scint eff vel has been recoordinated for this material before
    db = RAT.DB.Get(
    db.LoadAll(os.environ["GLG4DATA"], "*EFFECTIVE_VELOCITY*.ratdb")
    link = db.GetLink("EFFECTIVE_VELOCITY", material)
    try:
        current_vel = link.GetD("inner_av_velocity")
    except:
        got_value = False
    else:
        got_value = True

    if got_value:
        sev_filename = "{0}/sev_values.root".format(out_dir)
        sev_file = TFile(sev_filename)
 
        try:
            sev_vec = sev_file.GetObject("sev_vec")
        except:
            sev_vec = ROOT.TVector3()
        round_num = sev_vec.size()
        prev_value = sev_vec.back()
        sev_vec.push_back(current_vel)
        sev_file.delete("sev_vector")
        sev_vec.Write("sev_vector")
        print("Round ", round_num, ": ", current_vel)

        if ( abs(current_vel-prev_vel) / prev_value < 0.0005 ):
            return 0

    ## re-recoordinate scint effective velocities
    scint_eff_vel.setup_recon_jobs("SEV_Recon_Round{0}".format(round_num), out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir, geo_file, av_shift)

    ## recoordinate multipdff
    multipdf.setup_recon_jobs("MultiPDF_Recon_Round{0}".format(round_num), out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir)

    return 1
