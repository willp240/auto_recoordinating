import sys
import os
import string
import argparse
import simulation
import utilities

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Launch a load of identical rat simulation jobs")
    parser.add_argument('out_dir', type=str, help='directory to place reprocessed files')
    parser.add_argument('-e', '--env_file', type=str,
                        help='path to environment file',
                        default="/path/to/environment/env.sh")
    parser.add_argument("-s", "--submission_directory", type=str,
                       default="/path/to/this/repository/rat_submission/",
                       help="path to the directory this file is in, for outputs and inputs")
    parser.add_argument("-r", "--run_directory", type=str,
                       default="/path/to/rat/",
                       help="base directory from which the scripts will be run")
    parser.add_argument("-m", "--material", type=str,
                       default="labppo_2p2_scintillator",
                       help="which material are we recoordinating for?")
    args = parser.parse_args()

    ## check if output and condor directories exist, create if they don't
    out_dir = utilities.check_dir(args.out_dir)
    dag_dir = utilities.check_dir("{0}/dag/".format(out_dir))

    main_dag = string.Template(open("{0}/dag/main.dag".format(args.submission_directory), "r").read())
    main_dag_text = main_dag.substitute(dag_dir=dag_dir)
    main_dag_name = "{0}/main.dag".format(dag_dir)
    with open(main_dag_name, "w") as main_dag_file:
        main_dag_file.write(main_dag_text)

    #condor_directory = "{0}/condor".format(args.submission_directory)

    ### Initial simulation phase

    simulation.setup_jobs("e2p5MeV_sim",  out_dir, args.material, args.run_directory, args.env_file, True, 2.5)
    simulation.setup_jobs("e10p0MeV_sim", out_dir, args.material, args.run_directory, args.env_file, True, 10.0)

    sub_command = "condor_submit_dag {0}/main.dag".format(dag_dir)
    os.system(sub_command)

    ## repeat for 10 MeV
