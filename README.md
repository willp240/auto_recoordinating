# auto_recoordinating

Tool for automating position fitter recoordination process at SNO+. Will get put in rat-tools when done.
Who knows, maybe when it's all working we can add in energy and classifiers?

Lez doo diz


Main script submit_dagman calls fuctions to setup the jobs and write the dagman. There are different functions for simulation, and reconstruction and analysis for Quad, Scint Eff Vel and MultiPDF.

After the ScintEffVel/MPDF loop a script is run to see if the velocity has converged (changed < 0.05%). If it hasn't the script returns an error, triggering the rerunning of the loop. ScintEffVel and MPDF are run in a separate subdag to facilitate this behaviour.

Once covnergence is reached, ScintEffVel is also recoordinated at a higher energy (10 MeV) to recoordinate the interpolation by nhits.

Finally, fit performance tools are ran for 2.5MeV e-, plotting in r and z, and 1-10 MeV e-, plotting on r, z, and e (only using events with R < 4m for e)