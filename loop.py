import string
import sys
import os
import utilities

### Just make ${dag_dir}/iterate_loop.sh
### so have a template already made and fill out

### iterate_loop.sh will call a python script
### That python script will get the sev value, and push back a vector fron Utilities
### Can print it to screen if we like. At end of everything we should print them all out
### If change <X% return 0, else return 1
### If returning 1, we also need to call scint_eff_vel.setup_recon_jobs and multipdf.setup_recon_jobs with new round number in names


def setup_loop_script(out_dir, material, rat_root, env_file, sub_dir):

    ## copy loop script to output dir
    template_loop_filename = string.Template(open("{0}/dag/iterate_loop.sh".format(submission_dir), "r").read())
    template_loop_text = template_loop_filename.substitute(env_file=env_file,
                                                           sub_dir=sub_dir,
                                                           rat_root=rat_root,
                                                           material=material,
                                                           out_dir=out_dir
                                                           )
    main_loop_filename = "{0}/iterate_loop.sh".format(dag_dir)
    with open(main_loop_filename, "w") as main_loop_file:
        main_loop_file.write(template_loop_text)
