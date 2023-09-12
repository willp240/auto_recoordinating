# auto_recoordinating

Tool for automating position fitter recoordination process at SNO+. Uses HTCondor's DAGMan to submit sequential jobs to a batch system. It only works for HTCondor systems, if using a different system you'll need to use the individual FitCoordinationTools. This tool uses those same tools, but in requiring minimum input and efficient use of simulation.

## Position Recoordination
To recoordinate the full position fitter, individual fitters must be recoordinated sequentially. Firstly, the Quad fitter is coordinated by recoonstructing 500 2.5 MeV e- events with Quad using 7 different light velocities. The mean radial bias is calculated for each velocity. A linear fit is used to determine the best fit velocity to minimise the radial bias.

ScintEffectiveVelocity and MultiPDF are then recoordinated, using the newly recoordinated Quad as an input. ScintEffectiveVelocity is coordinated with a very similar process to Quad, but 5000 events are used for each of 12 velocities, and these are reconstructed with MultiPDF.

MultiPDF is then recoordinated by calculating the time residuals for 100,000 2.5 MeV e- using the newly coordinated ScintEffectiveVelocity.

As the ScintEffectiveVelocity and MultiPDF recoordinations depend on each other, these steps are repeated until the ScintEffectiveVelocity changes by <0.05% between rounds of recoordination.

Finally, ScintEffectiveVelocity is recoordinated at a higher energy, if the nhit scaling of ScintEffectiveVelocity is required.

For more details on the mechanics of the position recoordination, see the READMEs in the individual FitCoordinationTools directories.

## DAGMan
DAGMan (Directed Acyclic Graphs Manager) cann be used to submit batches of jobs that only start running once a previous batch of jobs have all completed successfully. Complex workflows can be developed with different Parent <-> Child relationships. For more information on how to use DAGMan, see [here](https://indico.cern.ch/event/733513/contributions/3118598/attachments/1711374/2759120/EUCW18-DAGMan.pdf).

The position recoordination requires a substantial amount of jobs to be run, and more to be started once those have finished (and various ratdb tables manually updated). The code in this repository is designed to setup a dagman to run all the necessary recoordination jobs with one command, as well as automatically updating ratdb tables and producing the intermediate plots for each round. The use of DAGMan means the user does not have to babysit jobs, waiting to run scripts and submit more as soon as they have finished. This, along with the more efficient reuse of simulation should reduce the overall recoordination time.

## Structure
`submitDag.py` is the main script the user will run, with the following argummennts and options:

out_dir: Directory to place reprocessed files
[-e] : Path to environment file
[-s] : Path to this directory
[-r] : Base rat directory
[-m] : Which material are we recoordinating for?
[-g] : Geometry file to use - location relative to rat/data/
[-x] : Set z coordinate of AV centre. Overwrites shift set in geo file

The main dag file (`dag/main.dag`) gets written to the output directory. This contains the overall structure of the workflow, and is the main dag file that gets submitted. It contains paths to several splices, which are like mini segments of a dag file which are separated for readability. 

Within `submitDag.py`, several setup job functions (from `./job_sub/`) are called to write the submission scripts and dag splices for each stage of the recoordination. Firstly, simulation is ran, which is then reconstructed with the various fitter jobs. These setup scripts either setup rat jobs, or rat-tools FitCoordination Analyse jobs.

The `dag/loop_sub.dag` subdag is also written to the output directory. The MultiPDF-SEV loop is in this subdag rather than a splice as subdags can be "retried" when exiting non-zero. This way, a loop structure is possible despite the "acyclic" in Directed Acyclic Graphs.

After the MultiPDF-SEV loop, a script is run to see if the velocity has converged (changed < 0.05%). If it hasn't the script returns an error, triggering the rerunning of the loop. This can happen up to ten times (DAGMan does not facilitate indefinite retries, but usually we only need 3 or 4 rounds of recoordination).

Plots from each stage of the recoordination processes are automatically made and saved using the FitCoordinationsTools options to do so.

Finally, fit performance tools are ran for 2.5MeV e-, plotting in r and z, and 1-10 MeV e-, plotting on r, z, and e (only using events with R < 4m for e).
