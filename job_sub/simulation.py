import string
import os
import sys
sys.path.append("./utils")
import utilities

### Writes the submission scripts and dag splices for running e- simulation jobs
### If fixed energy is true, e- have energy given by argument "energy"
### Otherwise they are uniform in range "energy" to "energy_high"
def setup_jobs(job_name, out_dir, material, rat_root, env_file, geo_file, av_shift, num_files, fixed_energy, energy, energy_high=10, r_min=0, r_max=4000):

    ## Make a condor submit file from template
    template_condor_filename = "template_files/template_condor.sub"
    template_condor_file = open(template_condor_filename, "r")
    template_condor_raw_text = string.Template(template_condor_file.read())

    ## Make bash file from template
    template_sh_filename = "template_files/template.sh"
    template_sh_file = open(template_sh_filename, "r")
    template_sh_raw_text = string.Template(template_sh_file.read())

    ### Setup output directories
    job_dir    = "{0}/{1}".format(out_dir,job_name)
    log_dir    = utilities.check_dir("{0}/log/".format(job_dir))
    error_dir  = utilities.check_dir("{0}/error/".format(job_dir))
    mac_dir    = utilities.check_dir("{0}/macros/".format(job_dir))
    sh_dir     = utilities.check_dir("{0}/sh/".format(job_dir))
    submit_dir = utilities.check_dir("{0}/submit/".format(job_dir))
    output_dir = utilities.check_dir("{0}/output/".format(job_dir))
    ## Use different rat macro depending on whether fixed or varying energy
    if fixed_energy == True:
        macro  = string.Template(open("rat_mac/fixed_e_sim.mac", "r").read())
        energy_string = str(energy)
    else:
        macro  = string.Template(open("rat_mac/var_e_sim.mac", "r").read())
        energy_string = str(energy) + " " + str(energy_high)
    dag_splice_text = ""

    ## Now loop over number of jobs to run
    for i in range(num_files):

        ## First make the rat macro
        output_file = "{0}/{1}_{2}.root".format(job_dir, job_name, i)
        macro_text = macro.substitute(ExtraDB="",
                                      ThinFactor=1.0,
                                      ScintMaterial=material,
                                      GeoFile=geo_file,
                                      AVShift=av_shift,
                                      FileName=output_file,
                                      Energy=energy_string,
                                      R_Min=str(r_min),
                                      R_Max=str(r_max),
                                      num_events=utilities.num_evs_per_file)
        macro_name = "{0}/{1}_{2}.mac".format(mac_dir, job_name, i)
        with open(macro_name, "w") as macro_file:
            macro_file.write(macro_text)

        ## And write the bash file to run
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
