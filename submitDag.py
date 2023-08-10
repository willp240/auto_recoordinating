import sys
import os
import string
import argparse

def write_macro(mac, macname, outfile):
    with open(macname, "w") as f:
        f.write(mac.format(os.path.abspath(outfile)))

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

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Launch a load of identical rat simulation jobs")
    parser.add_argument('macro', type=str, help='template macro file to load')
    parser.add_argument('out_dir', type=str, help='directory to place reprocessed files')
    parser.add_argument('-e', '--env_file', type=str,
                        help='path to environment file',
                        default="/path/to/environment/env.sh")
    parser.add_argument("-s", "--submission_directory", type=str,
                       default="/path/to/this/repository/rat_submission/",
                       help="path to the directory this file is in, for outputs and inputs")
    parser.add_argument("-d", "--run_directory", type=str,
                       default="/path/to/rat/",
                       help="base directory from which the scripts will be run")
    parser.add_argument("-m", "--material", type=str,
                       default="labppo_2p2_scintillator",
                       help="which material are we recoordinating for?")
    args = parser.parse_args()

    ## check if output and condor directories exist, create if they don't
    out_dir = check_dir(args.out_dir)
    rat_env_file = "{0}/env.sh".format(args.run_directory)

    #condor_directory = "{0}/condor".format(args.submission_directory)

    ## Make a condor submit file from template
    template_condor_filename = "{0}/template_condor.sub".format(args.submission_directory)
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ## Make .sh file from template
    template_sh_filename = "{0}/template.sh".format(args.submission_directory)
    template_sh_file = open(template_sh_filename, "r")
    template_sh_raw_text = string.Template(template_sh_file.read())

    ### Initial simulation phase

    ### 2.5 MeV dir
    e2p5mev_job_name   = "e2p5mev_sim"
    e2p5mev_dir = "{0}/{1}".format(out_dir,e2p5mev_job_name)
    e2p5mev_log_dir    = check_dir("{0}/log/".format(e2p5mev_dir))
    e2p5mev_error_dir  = check_dir("{0}/error/".format(e2p5mev_dir))
    e2p5mev_mac_dir    = check_dir("{0}/macros/".format(e2p5mev_dir))
    e2p5mev_sh_dir     = check_dir("{0}/sh/".format(e2p5mev_dir))
    e2p5mev_submit_dir = check_dir("{0}/submit/".format(e2p5mev_dir))
    e2p5mev_output_dir = check_dir("{0}/output/".format(e2p5mev_dir))
    e2p5mev_macro      = open("{0}/{1}.mac".format(args.submission_directory, e2p5mev_job_name), "r").read()

    for i in range(100):
        macro_text = e2p5mev_macro.substitute(output_file=e2p5mev_output_dir)
        macro_name = "{0}{1}_{2}.mac".format(e2p5mev_mac_dir, e2p5mev_job_name, i)
        with open(mac_name, "w") as mac_file:
            mac_file.write(macro_text)

        sh_text = template_sh_raw_text.substitute(env_file=args.env_file,
                                                  rat_env_file=rat_env_file,
                                                  mac_sub="{0}{1}_{2}.mac".format(e2p5mev_macro_dir, e2p5mev_job_name, i),
                                                  run_directory=args.run_directory)
        sh_name = "{0}{1}_{2}.sh".format(e2p5mev_sh_dir, e2p5mev_job_name, i)
        with open(sh_name, "w") as sh_file:
            sh_file.write(sh_text)
        
        sub_text = template_condor_raw_text.substitute(sh_file=sh_name,
                                                       error_file="{0}/error/{1}_{2}.error".format(e2p5mev_macro_dir,e2p5mev_job_name,i),
                                                       output_file="{0}/output/{1}_{2}.output".format(e2p5mev_macro_dir,e2p5mev_job_name,i),
                                                       log_file="{0}/log/{1}_{2}.log".format(e2p5mev_macro_dir,e2p5mev_job_name,i) )
        sub_name = "{0}{1}_{2}.sub".format(e2p5mev_sub_dir, e2p5mev_job_name, i)
        with open(sub_name, "w") as sub_file:
            sub_file.write(sub_text)

        dag_splice_line = "JOB e2p5MeV_sim_{0} {1}".format(i, sub_name)
        dag_splice_text += dag_splice_line+"\n"+\

    e2p5_dag_splice_name = "dag_dir/e2p5_sim.spl"
    with open(e2p5_dag_splice_name, "w") as e2p5_dag_splice:
            e2p5_dag_splice.write(dag_splice_text)

    universe = "vanilla"
    notification = "never"
    n_rep = 1
    getenv = "False" # "False"

    submit_filepath = os.path.join(submit_path, job_id)
    submit_filepath += ".submit"
    out_submit_text = "executable              = "+str(sh_filepath)+"\n"+\
                     "universe                = "+str(universe)+"\n"+\
                     "output                  = "+str(output_path)+"/"+str(job_id)+".output\n"+\
                     "error                   = "+str(error_path)+"/"+str(job_id)+".error\n"+\
                     "log                     = "+str(log_path)+"/"+str(job_id)+".log\n"+\
                     "notification            = "+str(notification)+"\n"+\
                     "priority                = "+str(priority)+"\n"+\
                     "getenv                  = "+str(getenv)+"\n"+\
                     "queue "+str(n_rep)+"\n"

    # remember to make the template rat and condor macros Bill

    ## Make dag file and and add 2.5MeV submissions (maybe in a splice I guess)
    with open("./dag_dir/e2p5MeV_sim.spl", "w") as dag_splice:
        dag_splice.write(mac.format(os.path.abspath(outfile)))

    ## repeat for 10 MeV
        


    for i in range(args.no_sims):
        write_macro(mac,
                    "{0}{1}_{2}.mac".format(mac_dir, base_name, i),
                    "{0}{1}_{2}.root".format(out_dir, base_name, i)
        )
        
        job_id = "{0}_{1}".format(base_name,i)
        batch_id = "rat_{0}".format(base_name)
        pycondor_submit(batch_id,job_id,"{0}{1}_{2}.mac".format(mac_dir,base_name,i),args.run_directory,args.env_file,args.submission_directory,out_dir, sleep_time = 1, priority = 5)
