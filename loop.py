import string
import sys
import os
import utilities

def setup_loop_script(out_dir, material, rat_root, env_file, sub_dir):

    ## copy loop script to output dir
    template_loop_filename = string.Template(open("{0}/dag/iterate_loop.sh".format(sub_dir), "r").read())
    template_loop_text = template_loop_filename.substitute(out_dir=out_dir,
                                                           env_file=env_file,
                                                           sub_dir=sub_dir,
                                                           rat_root=rat_root,
                                                           material=material,
                                                           bash_command="if [ $? != 0 ];")
    main_loop_filename = "{0}/dag/iterate_loop.sh".format(out_dir)
    with open(main_loop_filename, "w") as main_loop_file:
        main_loop_file.write(template_loop_text)

    os.chmod(main_loop_filename, 0o777)