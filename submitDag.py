import sys
sys.path.append("./job_sub")
sys.path.append("./utils")
import os
import string
import argparse
import simulation
import utilities
import quad
import scint_eff_vel
import multipdf
import loop
import db_utilities
import fit_perf
import rat
from ROOT import RAT
sys.path.append("/home/parkerw/Software/rat-tools_fork/FitCoordination/ScintEffectiveSpeed") #TODO fix this and below
import SEVUtilities
sys.path.append("/home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed")
import Utilities

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Launch jobs for recoordinating position fitters")
    parser.add_argument('out_dir', type=str, help='Directory to place reprocessed files')
    parser.add_argument('-e', '--env_file', type=str,
                        help='Path to environment file',
                        default="/path/to/environment/env.sh")
    parser.add_argument("-s", "--submission_directory", type=str,
                       default="/path/to/this/repository/rat-tools/FitCoordination/auto_recoordination",
                       help="Path to the directory this file is in, for outputs and inputs")
    parser.add_argument("-r", "--rat_root", type=str,
                       default="/path/to/rat/",
                       help="Base rat directory")
    parser.add_argument("-m", "--material", type=str,
                       default="labppo_2p2_scintillator",
                       help="Which material are we recoordinating for?")
    parser.add_argument("-g", "--geo_file", type=str, 
                        default = "geo/snoplusnative.geo",
                        help = "Geometry file to use - location relative to rat/data/")
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

    ## Copy main dag file to output dir
    main_dag = string.Template(open("{0}/dag/main.dag".format(submission_dir), "r").read())
    main_dag_text = main_dag.substitute(dag_dir=dag_dir)
    main_dag_name = "{0}/main.dag".format(dag_dir)
    with open(main_dag_name, "w") as main_dag_file:
        main_dag_file.write(main_dag_text)

    ## And do same for sub dag file
    sub_dag = string.Template(open("{0}/dag/loop_sub.dag".format(submission_dir), "r").read())
    sub_dag_text = sub_dag.substitute(dag_dir=dag_dir)
    sub_dag_name = "{0}/loop_sub.dag".format(dag_dir)
    with open(sub_dag_name, "w") as sub_dag_file:
        sub_dag_file.write(sub_dag_text)

    ## Check if this will be first time sev has been recoordinated for this material
    default_material = db_utilities.check_first_sev(material)

    ## Get SEV velocities and write to a file
    sev_vels = SEVUtilities.Speeds
    sev_vels_filename = "{0}/sev_velocities.txt".format(out_dir)
    sev_vels_file = open(sev_vels_filename, 'w')
    for vel in sev_vels:
        sev_vels_file.write(str(vel) + "\n")
    sev_vels_file.close()

    ## Get Quad velocities and write to a file
    quad_vels = Utilities.SpeedsScint
    quad_vels_filename = "{0}/quad_velocities.txt".format(out_dir)
    quad_vels_file = open(quad_vels_filename, 'w')
    for vel in quad_vels:
        quad_vels_file.write(str(vel) + "\n")
    quad_vels_file.close()

    ## Now going to write the dag files and job submission scripts

    ## Initial simulation 
    simulation.setup_jobs("e2p5MeV_sim",  out_dir, material, rat_root, env_file, geo_file, av_shift, utilities.sim_num_files, True, 2.5, 0, 0, 4000)
    simulation.setup_jobs("e10p0MeV_sim", out_dir, material, rat_root, env_file, geo_file, av_shift, utilities.sev_files_per_velocity*len(sev_vels), True, 10.0, 0, 0, 4000)

    ## Also the simulation for fit performance tools, may as well start the simulation now
    simulation.setup_jobs("perf_e2p5MeV_sim",  out_dir, material, rat_root, env_file, geo_file, av_shift, utilities.sim_num_files, True, 2.5, 0, 0, 5500)
    simulation.setup_jobs("perf_e1to10MeV_r4m_sim", out_dir, material, rat_root, env_file, geo_file, av_shift, utilities.sim_num_files, False, 1.0, 10.0, 0, 4000)
    simulation.setup_jobs("perf_e1to10MeV_sim", out_dir, material, rat_root, env_file, geo_file, av_shift, utilities.sim_num_files, True, 10.0, 0, 0, 5500)

    ## Recoordinate quad first
    quad.setup_recon_jobs("quad_recon", out_dir, "e2p5MeV_sim", material, rat_root, env_file, geo_file, av_shift, default_material, quad_vels)
    quad.setup_analyse_jobs("quad_analyse", "quad_recon", out_dir, material, rat_root, env_file, submission_dir) 

    ## Recoordinate scintillator effective velocity
    scint_eff_vel.setup_recon_jobs("sev_recon_round0", out_dir, "e2p5MeV_sim", False, material, rat_root, env_file, submission_dir, geo_file, av_shift, default_material, sev_vels)
    scint_eff_vel.setup_analyse_jobs("sev_analyse_round0", out_dir, "single_energy", "sev_recon_round0", "", material, rat_root, env_file, submission_dir)

    ## Recoordinate multiPDF
    multipdf.setup_recon_jobs("multiPDF_recon_round0", out_dir, "e2p5MeV_sim", material, rat_root, env_file, submission_dir)

    ## Script for iterating the scintillator effective velocity and multiPDF loop
    loop.setup_loop_script(out_dir, material, rat_root, env_file, submission_dir)

    ## Now reconstruct the higher energy files for scaling scintillator effective velocity
    scint_eff_vel.setup_recon_jobs("sev_recon_high_e", out_dir, "e10p0MeV_sim", True, material, rat_root, env_file, submission_dir, geo_file, av_shift, False, sev_vels)
    scint_eff_vel.setup_analyse_jobs("sev_analyse_high_e", out_dir, "interpolate", "sev_recon_round", "sev_recon_high_e", material, rat_root, env_file, submission_dir)

    ## Using the newly recooordinated fitters, reconstruct events for fit performance
    fit_perf.setup_recon_jobs("perf_e2p5MeV_recon", out_dir, "perf_e2p5MeV_sim", rat_root, env_file, submission_dir, av_shift)
    fit_perf.setup_recon_jobs("perf_e1to10MeV_recon", out_dir, "perf_e1to10MeV_sim", rat_root, env_file, submission_dir, av_shift)
    fit_perf.setup_recon_jobs("perf_e1to10MeV_r4m_recon", out_dir, "perf_e1to10MeV_r4m_sim", rat_root, env_file, submission_dir, av_shift)

    ## Finally, run the fit performance tools
    fit_perf.setup_tools_jobs("perf_e2p5MeV_tools", out_dir, "perf_e2p5MeV_recon", env_file, submission_dir, "r")
    fit_perf.setup_tools_jobs("perf_e2p5MeV_tools", out_dir, "perf_e2p5MeV_recon", env_file, submission_dir, "z")
    fit_perf.setup_tools_jobs("perf_e1to10MeV_tools", out_dir, "perf_e1to10MeV_recon", env_file, submission_dir, "r")
    fit_perf.setup_tools_jobs("perf_e1to10MeV_tools", out_dir, "perf_e1to10MeV_recon", env_file, submission_dir, "z")
    ## Use different simulation when plotting as a function of energy. Only use events in 4m FV
    fit_perf.setup_tools_jobs("perf_e1to10MeV_tools", out_dir, "perf_e1to10MeV_r4m_recon", env_file, submission_dir, "e")

    ## We are now ready to submit the dag man
    sub_command = "condor_submit_dag {0}/main.dag".format(dag_dir)
    print(sub_command)
    os.system(sub_command)

