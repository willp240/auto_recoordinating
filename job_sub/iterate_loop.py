import sys
import argparse
sys.path.append("./job_sub/")
sys.path.append("./utils/")
import utilities
import scint_eff_vel
import multipdf

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Determine if ScintEffVel has converged and re-write dag and scripts if not")
    parser.add_argument('out_dir', type=str, help='directory to place reprocessed files')
    parser.add_argument('-e', '--env_file', type=str,
                        help='Path to environment file',
                        default="/path/to/environment/env.sh")
    parser.add_argument("-s", "--submission_directory", type=str,
                       default="/path/to/this/repository/rat_submission/",
                       help="Path to the directory this file is in, for outputs and inputs")
    parser.add_argument("-r", "--rat_root", type=str,
                       default="/path/to/rat/",
                       help="Base rat directory")
    parser.add_argument("-m", "--material", type=str,
                       default="labppo_2p2_scintillator",
                       help="Which material are we recoordinating for?")
    parser.add_argument("-g", "--geo_file", type=str, 
                        default = "geo/snoplusnative.geo",
                        help = "Geometry File to use - location relative to rat/data/")
    parser.add_argument("-x", "--extraAVShift", type=str, 
                        default = "",
                        help = "Set z coordinate of AV centre. Overwrites shift set in geo file")
    args = parser.parse_args()

    ## Check if output and condor directories exist, create if they don't
    out_dir = utilities.check_dir(args.out_dir)
    dag_dir = utilities.check_dir("{0}/dag/".format(out_dir))
    plot_dir = utilities.check_dir("{0}/plots/".format(out_dir))

    ## Getting arguments
    material = args.material
    rat_root = args.rat_root
    env_file = args.env_file
    submission_dir = args.submission_directory
    geo_file = args.geo_file
    av_shift = ""
    if args.extraAVShift:
        avShift = "/rat/db/set GEO[av] position [0.,0.," + args.extraAVShift + "]"

    ## Open file where we write the effective velocity for each round
    sev_filename = "{0}/sev_values.txt".format(out_dir)
    try:
        sev_file = open(sev_filename, 'r')
        sev_text = sev_file.read()
    except:
        sev_text = ""
    sev_list = sev_text.split()

    ## Get current round number from number of written velocities
    round_num = len(sev_list)

    ## Get current effective velocity
    curr_val = float(sev_list[round_num-1])

    ## If first round, rerun
    if round_num > 1:
        ## If not first round, see how much velocity has changed by
        prev_val = float(sev_list[round_num-2])
        pc_diff = 100 * abs(curr_val-float(prev_val)) / float(prev_val)

        ## Determine if change is small enough to satisfy convergence criteria
        if ( pc_diff < utilities.convergence_criteria ):
            ## If so exit with 0
            exit(0)

    ## If we've not yet converged, rewrite the dag and submission scripts
    ## Re-recoordinate scint effective velocities
    scint_eff_vel.setup_recon_jobs("sev_recon_round{0}".format(round_num), out_dir, "e2p5MeV_sim", False, material, rat_root, env_file, submission_dir, geo_file, av_shift, False)
    scint_eff_vel.setup_analyse_jobs("sev_analyse_round{0}".format(round_num), out_dir, "single_energy", "sev_recon_round{0}".format(round_num), "", material, rat_root, env_file, submission_dir)

    ## Re-recoordinate multiPDF
    multipdf.setup_recon_jobs("multiPDF_recon_round{0}".format(round_num), out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir)

    ## Exit with error 1 to trigger rerunning of loop
    exit(1)
