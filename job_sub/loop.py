import string
import os

## Setup the multiPDF-SEV loop script and copy to output directory
def setup_loop_script(out_dir, material, rat_root, env_file, sub_dir):

    ## Copy loop script to output dir and update it
    template_loop_filename = string.Template(open("{0}/dag/iterate_loop.sh".format(sub_dir), "r").read())
    template_loop_text = template_loop_filename.substitute(out_dir=out_dir,
                                                           env_file=env_file,
                                                           sub_dir=sub_dir,
                                                           rat_root=rat_root,
                                                           material=material,
                                                           bash_command="if [ $? != 0 ];",
                                                           sev_string_command="$(cat  $filename |tr \"\n\" \" \")",
                                                           sev_array_command="($sev_string)",
                                                           round_num_command="$((${#sev_array[@]} - 1))",
                                                           sh_file_string_command="$(cat {0}/sev_analyse_high_e/sh/sev_analyse_high_e.sh)".format(out_dir),
                                                           sed_command="sed -i \"s/$sub_str/$sub_str$round_num/\" ")
    main_loop_filename = "{0}/dag/iterate_loop.sh".format(out_dir)
    with open(main_loop_filename, "w") as main_loop_file:
        main_loop_file.write(template_loop_text)

    os.chmod(main_loop_filename, 0o777)