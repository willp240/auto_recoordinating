import string
import os
import sys
sys.path.append("./utils")
import utilities

### Writes the submission scripts and dag splices for reconstructing with SEV
### If high_e is True, outputted files have high_e in name for scaling by nhits
def setup_recon_jobs(job_name, out_dir, infile, high_e, material, rat_root, env_file, submission_dir, geo_file, av_shift, defaultMaterial, speeds):

    ## Make a condor submit file from template
    template_condor_filename = "template_files/template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ## Make bash file from template
    template_sh_filename = "template_files/template.sh"
    template_sh_file = open(template_sh_filename, "r")
    template_sh_raw_text = string.Template(template_sh_file.read())

    ## Setup output directories
    job_dir    = "{0}/{1}".format(out_dir, job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    mac_dir    = utilities.check_dir("{0}/macros/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))
    macro      = string.Template(open("/home/parkerw/Software/rat-tools_fork/FitCoordination/ScintEffectiveSpeed/Template_Macro_Inroot.mac", "r").read()) #TODO fix this eventually
    dag_splice_text = ""

    ## Change output file prefix depending on if we want this to be the high or low energy
    if high_e == False:
        file_prefix=""
    else:
        file_prefix="highE_"

    ## We will count how many input files we've looped over, so we can ensure each veocity gets independent files 
    file_count = 0

    ## Now run these macros over the simulation (with diff velocities)
    for i in speeds:

        ## Loop over input files
        input_file = ""
        input_command = ""
        for infile_num in range(utilities.sev_files_per_velocity):
            input_file += input_command + " " + out_dir + "/" + infile + "/" + infile + "_" + str(file_count) + ".root\n"
            input_command = "/rat/inroot/load"
            file_count += 1

        ## Make the rat macro
        output_file = "{0}/{1}scintFit_{2}.root".format(job_dir, file_prefix, str(i))
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

        ## And make the bash file to run
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
        dag_splice_name = "{0}/dag/sev_recon_high_e.spl".format(out_dir)

    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)

### Writes the submission scripts and dag splice for running job to analyse SEV files
### e_choice determines if we want to scale by nhits or not
### low_e_input_files and high_e_input_files are the locations of the reconstructed files
def setup_analyse_jobs(job_name, out_dir, e_choice, low_e_input_files, high_e_input_files, material, rat_root, env_file, submission_dir):

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

    input_files_low_e = "{0}/{1}/".format(out_dir, low_e_input_files)
    input_files_high_e = "{0}/{1}/".format(out_dir, high_e_input_files)

    ## Make bash file from template
    template_analyse_filename = "template_files/template_analyse_sev.sh"
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
    if e_choice == "single_energy":
        dag_splice_name = "{0}/dag/sev_analyse.spl".format(out_dir)
    else:
        dag_splice_name = "{0}/dag/sev_analyse_high_e.spl".format(out_dir)
    dag_splice_text = "JOB {0} {1}".format( job_name, sub_name)
    with open(dag_splice_name, "w") as dag_splice:
        dag_splice.write(dag_splice_text)
