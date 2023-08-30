import sys
import os
import string
import argparse
import utilities
import scint_eff_vel
import multipdf

if __name__ == "__main__":

    file1 = open("/home/parkerw/Software/auto_recoordinating/test.txt", "a")  # append mode
    file1.write("in the python script ok \n")

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

    file1.write("parsed args \n")

    ## check if output and condor directories exist, create if they don't
    out_dir = utilities.check_dir(args.out_dir)
    dag_dir = utilities.check_dir("{0}/dag/".format(out_dir))
    plot_dir = utilities.check_dir("{0}/plots/".format(out_dir))

    material = args.material
    rat_root = args.rat_root
    env_file = args.env_file
    submission_dir = args.submission_directory
    geo_file = args.geo_file
    av_shift = ""
    if args.extraAVShift:
        avShift = "/rat/db/set GEO[av] position [0.,0.," + args.extraAVShift + "]"

    sev_filename = "{0}/sev_values.txt".format(out_dir)
    try:
        sev_file = open(sev_filename, 'r')
        sev_text = sev_file.read()
    except:
        sev_text = ""
    sev_list = sev_text.split()
    file1.write("current list " + sev_text + "\n")
    round_num = len(sev_list)
    file1.write("round "+ str(round_num) + "\n")
    if round_num > 1:
        prev_val = sev_list[round_num-2]
        curr_val = sev_list[round_num-1]

        pc_diff = 100 * abs(curr_val-float(prev_val)) / float(prev_val)
        file1.write("% diff: ", pc_diff)
        if ( pc_diff < 1 ):
            file1.write("exiting 0\n")
            exit(0)

    ## re-recoordinate scint effective velocities
    scint_eff_vel.setup_recon_jobs("sev_recon_Round{0}".format(round_num+1), out_dir, "e2p5MeV_Sim", material, rat_root, env_file, submission_dir, geo_file, av_shift)

    ## recoordinate multipdff
    multipdf.setup_recon_jobs("multiPDF_recon_Round{0}".format(round_num+1), out_dir, "e2p5MeV_Sim", material, rat_root, env_file, submission_dir)
    file1.write("setup jobs\n")
    file1.write("exiting 1\n")
    file1.close()
    exit(1)
