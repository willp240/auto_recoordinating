import string
import sys
import os
import utilities

def setup_recon_jobs(job_name, out_dir, infile, material, rat_root, env_file, submission_dir, geo_file, av_shift):

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
    macro      = string.Template(open("/home/parkerw/Software/rat-tools_fork/FitCoordination/ScintEffectiveSpeed/Template_Macro_Inroot.mac", "r").read()) #TODO fix this eventually
    dag_splice_text = ""

    input_file = out_dir + "/" + infile + "/" + infile + "_0.root"

    ## Now loop over number of jobs to run
    for i in range(5):

        ## First make the rat macro
        output_file = "{0}/{1}_{2}.root".format(job_dir, job_name, i)
        macro_text = macro.substitute(ExtraDB="",
                                      ThinFactor=1.0,
                                      GeoFile=geo_file,
                                      ScintMaterial=material,
                                      SpeedDB="",
                                      ScaledDB="",
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
                                                  sleep = "$((1 + $RANDOM % 10))",
                                                  out_dir=out_dir,
                                                  sub_dir=submission_dir)
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
