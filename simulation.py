import string
import sys
import os
import utilities

def setup_jobs(job_name, out_dir, material, rat_root, env_file, geo_file, av_shift, fixed_energy, energy):

    ## Make a condor submit file from template
    template_condor_filename = "template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ## Make .sh file from template
    template_sh_filename = "template.sh"
    template_sh_file = open(template_sh_filename, "r")
    template_sh_raw_text = string.Template(template_sh_file.read())

    ### setup output directories
    job_dir    = "{0}/{1}".format(out_dir,job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    mac_dir    = utilities.check_dir("{0}/macros/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))
    macro      = string.Template(open("fixed_e_sim.mac", "r").read())
    dag_splice_text = ""

    for i in range(5):
        output_file = "{0}/{1}_{2}.root".format(job_dir, job_name, i)
        macro_text = macro.substitute(ExtraDB="",
                                      ThinFactor=1.0,
                                      ScintMaterial=material,
                                      GeoFile=geo_file,
                                      AVShift=av_shift,
                                      FileName=output_file,
                                      Energy=energy)
        macro_name = "{0}/{1}_{2}.mac".format(mac_dir, job_name, i)
        with open(macro_name, "w") as macro_file:
            macro_file.write(macro_text)

        sh_text = template_sh_raw_text.substitute(env_file=env_file,
                                                  rat_root=rat_root,
                                                  macro_name="{0}{1}_{2}.mac".format(mac_dir, job_name, i))
        sh_name = "{0}{1}_{2}.sh".format(sh_dir, job_name, i)
        with open(sh_name, "w") as sh_file:
            sh_file.write(sh_text)
        os.chmod(sh_name, 0o777)

        sub_text = template_condor_raw_text.substitute(sh_file=sh_name,
                                                       error_file="{0}/{1}_{2}.error".format(error_dir, job_name, i),
                                                       output_file="{0}/{1}_{2}.output".format(output_dir, job_name, i),
                                                       log_file="{0}/{1}_{2}.log".format(log_dir, job_name, i))
        sub_name = "{0}{1}_{2}.sub".format(submit_dir, job_name, i)
        with open(sub_name, "w") as sub_file:
            sub_file.write(sub_text)

        dag_splice_line = "JOB {0}_{1} {2}".format( job_name, i, sub_name)
        dag_splice_text += dag_splice_line+"\n"

    dag_splice_name = "{0}/dag/{1}.spl".format(out_dir, job_name)
    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)
