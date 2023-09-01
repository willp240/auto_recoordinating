import string
import sys
import os
import utilities

def setup_recon_jobs(job_name, out_dir, infile, high_e, material, rat_root, env_file, submission_dir, geo_file, av_shift, defaultMaterial):


    speeds = utilities.SEVSpeeds

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

    if high_e == False:
        file_suffix=""
    else:
        file_suffix="high_"

    input_file = out_dir + "/" + infile + "/" + infile + "_0.root"

    ## Now run these macros over some simulation (with diff velocities)
    for i in speeds:

        ## First make the rat macro
        output_file = "{0}/scintFit_{1}{2}.root".format(job_dir, file_suffix, str(i))
        if defaultMaterial:
            speed_string = "EFFECTIVE_VELOCITY inner_av_velocity %s" % i
            scaled_string = "EFFECTIVE_VELOCITY scale_inner_av_vel false"
        else:
            speed_string = "EFFECTIVE_VELOCITY[%s] inner_av_velocity %s" % (material, i)
            scaled_string = "EFFECTIVE_VELOCITY[%s] scale_inner_av_vel false" % material
        macro_text = macro.substitute(ExtraDB="",
                                      ThinFactor=1.0,
                                      GeoFile=geo_file,
                                      ScintMaterial=material,
                                      SpeedDB=speed_string,
                                      ScaledDB=scaled_string,
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
    if high_e == False:
        dag_splice_name = "{0}/dag/sev_recon.spl".format(out_dir)
    else:
        dag_splice_name  = "{0}/dag/sev_recon_high_e.spl".format(out_dir)

    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)


def setup_analyse_jobs(job_name, out_dir, e_choice, low_e_input_files, high_e_input_files, material, rat_root, env_file, submission_dir):

#   # Make a condor submit file from template
    template_condor_filename = "template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ### Setup output directories
    job_dir    = "{0}/{1}".format(out_dir, job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))

    ## Write dag splice to file
    if e_choice == "single_energy":
        dag_splice_name = "{0}/dag/sev_recon.spl".format(out_dir)
        analyse_job_name = "sev_analyse"
    else:
        dag_splice_name  = "{0}/dag/sev_recon_high_e.spl".format(out_dir)
        analyse_job_name = "sev_analyse_high_e"

    input_files_low_e = "{0}/{1}/".format(out_dir, low_e_input_files)
    input_files_high_e = "{0}/{1}/".format(out_dir, high_e_input_files)

    ## Make .sh file from template
    template_analyse_filename = "template_analyse_sev.sh"
    template_analyse_sh_file = open(template_analyse_filename, "r")
    template_analyse_sh_raw_text = string.Template(template_analyse_sh_file.read())
    analyse_sh_text = template_analyse_sh_raw_text.substitute(env_file=env_file,
                                                              rat_root=rat_root,
                                                              submission_dir=submission_dir,
                                                              material=material,
                                                              energy_choice=e_choice,
                                                              input_files=input_files_low_e,
                                                              input_files_high=input_files_high_e,
                                                              plot_dir="{0}/plots".format(out_dir),
                                                              sleep="$((1 + $RANDOM % 10))",
                                                              out_dir=out_dir,
                                                              sub_dir=submission_dir
                                                              )

    analyse_sh_name = "{0}/{1}.sh".format(sh_dir, analyse_job_name)
    with open(analyse_sh_name, "w") as analyse_file:
        analyse_file.write(analyse_sh_text)
    os.chmod(analyse_sh_name, 0o777)

    ## And the condor submission macro
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
