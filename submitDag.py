import sys
import os
import string
import argparse
import simulation
import utilities
import quad
import scint_eff_vel
import multipdf

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
    av_shift = ""
    if args.extraAVShift:
        avShift = "/rat/db/set GEO[av] position [0.,0.," + args.extraAVShift + "]"

    ## copy main dag file to output dir
    main_dag = string.Template(open("{0}/dag/main.dag".format(submission_dir), "r").read())
    main_dag_text = main_dag.substitute(dag_dir=dag_dir)
    main_dag_name = "{0}/main.dag".format(dag_dir)
    with open(main_dag_name, "w") as main_dag_file:
        main_dag_file.write(main_dag_text)

    ## and do same for sub dag file
    sub_dag = string.Template(open("{0}/dag/loop_sub.dag".format(submission_dir), "r").read())
    sub_dag_text = sub_dag.substitute(dag_dir=dag_dir)
    sub_dag_name = "{0}/loop_sub.dag".format(dag_dir)
    with open(sub_dag_name, "w") as sub_dag_file:
        sub_dag_file.write(sub_dag_text)

    ### initial simulation phase

    simulation.setup_jobs("e2p5MeV_sim",  out_dir, material, rat_root, env_file, geo_file, av_shift, True, 2.5)
    #simulation.setup_jobs("e10p0MeV_sim", out_dir, material, rat_root, env_file, geo_file, av_shift, True, 10.0)

    ## recoordinate quad first
    quad.setup_recon_jobs("quad_recon", out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir, geo_file, av_shift)

    ## recoordinate scint effective velocities
    scint_eff_vel.setup_recon_jobs("sev_recon", out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir, geo_file, av_shift)

    ## recoordinate multipdff
    multipdf.setup_recon_jobs("multipdf_recon", out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir)

    sub_command = "condor_submit_dag {0}/main.dag".format(dag_dir)
    print(sub_command)
    os.system(sub_command)
