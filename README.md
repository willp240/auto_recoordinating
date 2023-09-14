NOTE: this repo is now deprecated as a pull request incorporating it into rat-tools has been made. Further developments will take place there 

# auto_recoordinating

Tool for automating the position fitter recoordination process at SNO+. Using HTCondor's DAGMan, sequential job are submitted to a batch system. It only works for HTCondor systems, so if you are using a different system you'll need to use the individual `FitCoordinationTools`. This tool uses those same tools, but requiring minimum user input and efficient use of simulation.

## Position Recoordination
To recoordinate the full position fitter, individual fitters must be recoordinated sequentially. Firstly, the `Quad` fitter is coordinated by reconstructing 500 2.5 MeV e- events with `Quad` using 7 different light velocities. The mean radial bias is calculated for each velocity. A linear fit is used to determine the best fit velocity to minimise the radial bias.

`ScintEffectiveVelocity` and `MultiPDF` are then recoordinated, using the newly recoordinated `Quad` as a seed. `ScintEffectiveVelocity` is coordinated with a very similar process to `Quad`, but 5000 events are used for each of 12 velocities, and these are reconstructed with `MultiPDF`.

`MultiPDF` is then recoordinated by calculating the time residuals for 100,000 2.5 MeV e- using the newly coordinated `ScintEffectiveVelocity`.

As the `ScintEffectiveVelocity` and `MultiPDF` recoordinations depend on each other, these steps are repeated until the `ScintEffectiveVelocity` changes by <0.05% between rounds of recoordination.

Finally, `ScintEffectiveVelocity` is recoordinated at a higher energy, if the nhit scaling of `ScintEffectiveVelocity` is required.

For more details on the mechanics of the position recoordination, see the `READMEs` in the individual `FitCoordinationTools` directories.

## DAGMan
DAGMan (Directed Acyclic Graphs Manager) can be used to submit batches of jobs that only start running once a previous batch of jobs have all completed successfully. Complex workflows can be developed with different Parent <-> Child relationships. For more information on how to use DAGMan, see [here](https://indico.cern.ch/event/733513/contributions/3118598/attachments/1711374/2759120/EUCW18-DAGMan.pdf).

The position recoordination requires a substantial amount of jobs to be run, and more to be started once those have finished (and various ratdb tables manually updated). The code in this repository is designed to setup a dagman to run all the necessary recoordination jobs with one command, as well as automatically updating ratdb tables and producing the intermediate plots for each round. The use of DAGMan means the user does not have to 'babysit' jobs, waiting to run scripts and submit more as soon as they have finished. This, along with the more efficient reuse of simulation significantly reduces the overall recoordination time.

## Structure
`submitDag.py` is the main script the user will run, with the following arguments and options:

out_dir: Directory to place reprocessed files\
[-e] : Path to environment file\
[-s] : Path to this directory\
[-r] : Base rat directory\
[-m] : Which material are we recoordinating for?\
[-g] : Geometry file to use - location relative to rat/data/\
[-x] : Set z coordinate of AV centre. Overwrites shift set in geo file\

The main dag file (`dag/main.dag`) gets written to the output directory. This contains the overall structure of the workflow, and is the over-arching dag that gets submitted. It contains paths to several splices, which are like mini-segments of a dag file which are separated for readability. 

Within `submitDag.py`, several setup job functions (from `./job_sub/`) are called to write the submission scripts and dag splices for each stage of the recoordination. Firstly, simulation is ran, which is then reconstructed with the various fitter jobs. These setup scripts either setup `RAT` jobs, or `FitCoordinationTools` `Analyse` jobs.

The `dag/loop_sub.dag` subdag is also written to the output directory. The `MultiPDF-ScintEffectiveVelocity` loop is in this subdag rather than a splice as subdags can be 'retried' when exiting non-zero. This way, a loop structure is possible despite the 'acyclic' in Directed Acyclic Graphs.

After the `MultiPDF-ScintEffectiveVelocity` loop, a script is run to see if the velocity has converged (changed < 0.05%). If it hasn't the script returns an error, triggering the rerunning of the loop. This can happen up to ten times (DAGMan does not facilitate indefinite retries, but usually we only need 3 or 4 rounds of recoordination).

Plots from each stage of the recoordination processes are automatically made and saved using the `FitCoordinationsTools` options to do so.

Finally, `FitPerformanceTools` are ran for 2.5MeV e-, plotting in `r` and `z`, and 1-10 MeV e-, plotting on `r`, `z`, and `e` (only using events with `R < 4m` for `e`).

# Known Issues/Deficiencies
This section is here to highlight stumbling blocks found when developing the code and explain workarounds used, and how they could be improved in the future. 

## Iteration Problems

As described, the `MultiPDF-ScintEffectiveVelocity` loop is iterated by running a 'post script' after the loop subdag. This post script is not submitted as a Condor job, but also isn't run on the interactive machine you submit from. On this 'no-man's-land' node, I had problems running or importing rat. Without being able to recreate the problem on interactive machines, it was difficult to debug. Perhaps I could have spent more time investigating what node I was on, what was already installed there, and why there was an issue (I suspect it was different version installs clashing), but instead invoked some pragmatic but inelegant workarounds. 

In this post script we want to compare the new `ScintEffectiveVelocity` to the previous round's. Without being able to import rat, I was not able to just read the current value from the ratdb file in the normal way (like in `utils/db_utilities.py`). Instead, I write each new effective velocity to a text file in the output directory. This is maybe not the end of the world, as I would have needed a way to get the previous value at this stage anyway, and it's nice to be able to immediately see how the velocity has progressed in one place.

We also want to be able to overwrite the loop splices in this script, so that when the loop is retried we don't write to the same place. For this, we need to know the `ScintEffectiveVelocities` to run over. But we can't just call `ScintEffectiveSpeed/SEVUtilities.Speeds`, as `ScintEffectiveSpeed/SEVUtilities` will want to import rat. Instead, I write the velocities to another text file, and then we can just read them when we need them. In theory, one could call `scint_eff_vel.setup_recon_jobs()` and 
give a list of velocities as a argument that doesn't match the list of velocities in `rat-tools/FitCoordination/ScintEffectiveSpeed/SEVUtilities.py` which would cause problems. But this works for now.

## Modularity

Currently the code recoordinates the whole position fitter process. In the future, we probably want to include the energy fitter and classifiers. This won't be too difficult or require any changes to the structure of the code, but if we did this it would be useful to have options on which fitters/classifiers are recoordinated when running. 

Relatedly, it would be useful to have an option to not simulate more events, but instead use presimulated events. This wouldn't take much effort to implement, and would be useful particularly for debugging when maybe you don't care too much about the simulation itself.

We would need to write `main.dag` and `loop_sub.dag` from scratch at run time if we had these options.

## Repeated Code

Particularly in the job submission scripts, there is a lot of similar code setting up the log files, macros, etc. Maybe these could be combined into a single function, but they all need slightly different things. I think it's ok for now but something to think about if we were making big changes.

## Writing to Bash Template Files

The `iterate_loop.sh` script gets filled out by `loop.py` with the `substitute` function. Because `substitute` looks for `$`'s in the target file, we can't initially have environment variables inside the template bash script. Instead we write them when doing the substitution. It's a bit clunky, as some of the fields that get substituted are the same every time, so you'd think they could be directly in the template. It works fine, it just reduces the readability.
