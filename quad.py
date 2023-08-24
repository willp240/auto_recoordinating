import string
import sys
import os
import utilities
import rat
from ROOT import RAT
sys.path.append("/home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed/") #TODO fix this eventually
import Utilities

def setup_recon_jobs(job_name, out_dir, infile, material, rat_root, env_file, submission_dir, geo_file, av_shift):

    ## Check if quad has been recoordinated for this material before
    db = RAT.DB.Get()
    db.LoadAll(os.environ["GLG4DATA"], "*QUAD*.ratdb")
    link = db.GetLink("QUAD_FIT", material)
    try:
        link.GetD("light_speed")
    except:
        defaultMaterial = True
    else:
        defaultMaterial = False

    ## Get speeds to run over
    [speeds, numEvents] = Utilities.GetSpeeds( material )

    ## Make a condor submit file from template
    template_condor_filename = "template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ## Make .sh file from template
    template_sh_filename = "template.sh"
    template_sh_file = open(template_sh_filename, "r")
    template_sh_raw_text = string.Template(template_sh_file.read())

    ### Setup output directories
    job_dir    = "{0}/{1}".format(out_dir, job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    mac_dir    = utilities.check_dir("{0}/macros/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))
    macro      = string.Template(open("/home/parkerw/Software/rat-tools_fork/FitCoordination/QuadSpeed/Template_Macro_Inroot.mac", "r").read()) #TODO fix this eventually
    dag_splice_text = ""

    input_file = out_dir + "/" + infile + "/" + infile + "_0.root"

    ## Now run these macros over some simulation (with diff velocities)
    for i in speeds:

        ## First make the rat macro
        output_file = "{0}/quadFit_{1}.root".format(job_dir, str(int(i)))
        if defaultMaterial:
            speed_string = "QUAD_FIT light_speed %s" % i
        else:
            speed_string = "QUAD_FIT[%s] light_speed %s" % (material, i)
        macro_text = macro.substitute(ExtraDB="",
                                      ThinFactor=1.0,
                                      GeoFile=geo_file,
                                      ScintMaterial=material,
                                      SpeedDB=speed_string,
                                      AVShift=av_shift,
                                      InputFileName=input_file,
                                      FileName=output_file)
        macro_name = "{0}/{1}_{2}.mac".format(mac_dir, job_name, i)
        with open(macro_name, "w") as macro_file:
            macro_file.write(macro_text)

        ## And make the sh file to run
        sh_text = template_sh_raw_text.substitute(env_file=env_file,
                                                  rat_root=rat_root,
                                                  macro_name="{0}{1}_{2}.mac".format(mac_dir, job_name, i),
                                                  sleep = "$((1 + $RANDOM % 10))")
        sh_name = "{0}{1}_{2}.sh".format(sh_dir, job_name, i)
        with open(sh_name, "w") as sh_file:
            sh_file.write(sh_text)
        os.chmod(sh_name, 0o777)

        ## And the condor submission macro
        sub_text = template_condor_raw_text.substitute(sh_file=sh_name,
                                                       error_file="{0}/{1}_{2}.error".format(error_dir, job_name, i),
                                                       output_file="{0}/{1}_{2}.output".format(output_dir, job_name, i),
                                                       log_file="{0}/{1}_{2}.log".format(log_dir, job_name, i))
        sub_name = "{0}{1}_{2}.sub".format(submit_dir, job_name, i)
        with open(sub_name, "w") as sub_file:
            sub_file.write(sub_text)

        ## Finally add to the dag splice
        dag_splice_line = "JOB {0}_{1} {2}".format( job_name, i, sub_name)
        dag_splice_text += dag_splice_line+"\n"

    ## Write dag splice to file
    dag_splice_name = "{0}/dag/{1}.spl".format(out_dir, job_name)
    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)

    ## Now run analyse data funcs over these files, in the dag file

    ## Make .sh file from template
    template_analyse_filename = "template_analyse_quad.sh"
    template_analyse_sh_file = open(template_analyse_filename, "r")
    template_analyse_sh_raw_text = string.Template(template_analyse_sh_file.read())
    analyse_sh_text = template_analyse_sh_raw_text.substitute(env_file=env_file,
                                                              rat_root=rat_root,
                                                              submission_dir = submission_dir,
                                                              material = material,
                                                              input_files = "{0}/{1}/".format(out_dir, job_name),
                                                              plot_dir = "{0}/plots".format(out_dir),
                                                              sleep = "$((1 + $RANDOM % 10))")


    analyse_sh_name = "{0}/quad_analyse.sh".format(sh_dir)
    with open(analyse_sh_name, "w") as analyse_file:
        analyse_file.write(analyse_sh_text)
    os.chmod(analyse_sh_name, 0o777)

     ## And the condor submission macro
    analyse_job_name = "quad_analyse"
    sub_text = template_condor_raw_text.substitute(sh_file=analyse_sh_name,
                                                   error_file="{0}/{1}.error".format(error_dir, analyse_job_name),
                                                   output_file="{0}/{1}.output".format(output_dir, analyse_job_name),
                                                   log_file="{0}/{1}.log".format(log_dir, analyse_job_name))
    sub_name = "{0}{1}.sub".format(submit_dir, analyse_job_name)
    with open(sub_name, "w") as sub_file:
        sub_file.write(sub_text)

    ## Write dag splice to file
    dag_splice_text = "JOB {0} {1}".format( analyse_job_name, sub_name)
    dag_splice_name = "{0}/dag/{1}.spl".format(out_dir, analyse_job_name)
    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)
