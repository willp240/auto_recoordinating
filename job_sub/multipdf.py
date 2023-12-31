import string
import os
import sys
sys.path.append("./utils")
import utilities

### Writes the submission scripts and dag splices for reconstructing and analysing with multiPDF
def setup_recon_jobs(job_name, out_dir, input_file, material, rat_root, env_file, submission_dir):

    ## Make a condor submit file from template
    template_condor_filename = "template_files/template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ### Setup output directories
    job_dir    = "{0}/{1}".format(out_dir, job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))

    ## Make bash file from template
    template_analyse_filename = "template_files/template_analyse_mpdf.sh"
    template_analyse_sh_file = open(template_analyse_filename, "r")
    template_analyse_sh_raw_text = string.Template(template_analyse_sh_file.read())
    analyse_sh_text = template_analyse_sh_raw_text.substitute(env_file=env_file,
                                                              rat_root=rat_root,
                                                              submission_dir = submission_dir,
                                                              material = material,
                                                              input_files = "{0}/{1}/".format(out_dir, input_file),
                                                              input_basename = input_file,
                                                              plot_dir = "{0}/plots".format(out_dir))

    analyse_sh_name = "{0}/{1}.sh".format(sh_dir, job_name)
    with open(analyse_sh_name, "w") as analyse_file:
        analyse_file.write(analyse_sh_text)
    os.chmod(analyse_sh_name, 0o777)

    ## And the condor submission macro
    sub_text = template_condor_raw_text.substitute(sh_file=analyse_sh_name,
                                                   error_file="{0}/{1}.error".format(error_dir, job_name),
                                                   output_file="{0}/{1}.output".format(output_dir, job_name),
                                                   log_file="{0}/{1}.log".format(log_dir, job_name))
    sub_name = "{0}{1}.sub".format(submit_dir, job_name)
    with open(sub_name, "w") as sub_file:
        sub_file.write(sub_text)

    ## Write dag splice to file
    dag_splice_text = "JOB {0} {1}".format( job_name, sub_name)
    dag_splice_name = "{0}/dag/multipdf_recon.spl".format(out_dir)
    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)
