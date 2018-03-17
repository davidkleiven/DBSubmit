import datetime
import subprocess
try:
    import settings
except ImportError:
    raise ImportError("Could not find settings file. You have to run the config script before installing the package.")

class Submit(object):
    def __init__( self, arguments ):
        self.args = arguments
        self.scriptnames = []
        self.runIds = []

    def getJobIDs( self ):
        raise NotImplementedError("This is specific to the application and has to be implemented in child classes")

    def updateDB( self, jobID ):
        raise NotImplementedError("This is specific to the application and has to be implemented in child classes")

    def generate_vilje( self, scriptname, runID ):
        """
        Generates a job script for the PBS system
        """
        with open(scriptname, 'w') as of:
            of.write("#!/bin/bash\n")
            of.write("#PBS -N %s\n"%(self.args["name"]) )
            of.write("#PBS -l walltime=%s\n"%(self.args["walltime"]) )
            of.write("#PBS -l select=%d:ncpus=32:mpiprocs=%d\n"%(self.args["nodes"],self.args["nproc"]) )
            of.write("#PBS -A %s\n"%(self.args["projID"]) )

            # Export paths
            of.write("module load intelcomp/17.0.0 mpt/2.14\n")
            of.write("module load python/2.7.13\n")
            of.write('export LD_LIBRARY_PATH="/usr/lib64":"/home/ntnu/davidkl/.local/lib":${LD_LIBRARY_PATH}\n')
            of.write('export GPAW_SETUP_PATH="/home/ntnu/davidkl/GPAW/gpawData/gpaw-setups-0.9.20000"\n')
            of.write('export PATH=${PATH}:"/home/ntnu/davidkl/.local/bin"\n')
            of.write('export PYTHONPATH=${PYTHONPATH}:"/home/ntnu/davidkl/.local/lib/python2.7/site-packages/ase-3.15.0b1-py2.7.egg"\n')
            of.write('export PYTHONPATH=${PYTHONPATH}:"/home/ntnu/davidkl/.local/lib/python2.7/site-packages/"\n')
            of.write( "cd %s\n"%(self.args["workdir"]) )
            of.write( "mpirun -np %d %s %s %d %s\n"%(self.args["nodes"]*self.args["nproc"], self.args["command"], self.args["main"], runID, self.arguments["args"]) )

    def generate_stallo( self, scriptname, runID ):
        """
        Generates job script for Stallo cluster
        """
        walltime = self.args["walltime"]
        split = walltime.split(":")
        hours = int(split[0])
        minutes = int(split[1])
        sec = int(split[2])
        days = int(hours/24)
        hours = hours - 24*days
        walltime = "%d-%d:%d:%d"%(days,hours,minutes,sec)

        with open(scriptname, 'w') as of:
            of.write("#!/bin/bash\n")
            of.write("#SBATCH --job-name=%s\n"%(self.args["name"]) )
            of.write("#SBATCH --time=%s\n"%(walltime))
            of.write("#SBATCH --nodes=%d\n"%(self.args["nodes"]))
            of.write("#SBATCH --ntasks-per-node=%d\n"%(self.args["nproc"]))
            of.write("#SBATCH --account=%s\n"%(self.args["projID"]))
            of.write("module purge\n")
            of.write("module load FFTW/3.3.6-intel-2016b\n")
            of.write("module load intel/2016b\n")
            of.write("module load Python/2.7.12-intel-2016b\n")
            of.write('export PATH=${PATH}:"/home/davidkl/.local/bin"\n')
            of.write('export PYTHONPATH=${PYTHONPATH}:"/home/davidkl/.local/lib/python2.7/site-packages"\n')
            of.write('export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:"/home/davidkl/.local/lib"\n')
            of.write('GPAW_SETUP_PATH="/home/davidkl/gpaw-setups-0.9.20000"\n')
            of.write("WORKDIR=%s\n"%(self.args["workdir"]))
            of.write("cd ${WORKDIR}\n")
            of.write("mpirun -np $SLURM_NTASKS %s %s %d %s\n"%(self.args["command"],self.args["main"],runID,self.arguments["args"]))

    def generate( self ):
        """
        Generates the job script
        """
        ids = self.getJobIDs()

        timestamp = datetime.datetime.today().strftime( "%Y%m%d_%H%M%S")
        for i in range(len(ids)):
            runID = int( ids[i] )
            self.runIds.append(runID)
            scriptname = self.args["workdir"]+"/job_%s_%d.sh"%(timestamp,i)
            self.scriptnames.append(scriptname)
            if ( settings.cluster == "vilje" ):
                self.generate_vilje( scriptname, runID )
            elif ( settings.cluster == "stallo" ):
                self.generate_stallo( scriptname, runID )
            elif( settings.cluster == "placeholder" ):
                self.generate_stallo( scriptname, runID )
            else:
                raise ValueError("Unknown computing cluster!")

    def submit( self ):
        self.generate()

        if ( self.args["njobs"] == -1 ):
            maxjobs = 100000
        else:
            maxjobs = int( self.args["njobs"] )
        number_submitted = 0
        print ("Starting maximum: %d jobs"%(maxjobs))
        for script,runID in zip(self.scriptnames,self.runIds):
            if ( number_submitted >= maxjobs ):
                return
            command = ""
            if ( settings.cluster == "vilje" ):
                command = "qsub"
            elif ( settings.cluster == "stallo" ):
                command = "sbatch"
            elif ( settings.cluster == "placeholder" ):
                command = "bin/sbatch_placeholder"
            else:
                raise ValueError("Unknown computing cluster!")
            subprocess.call( [command, script] )
            self.updateDB( runID )
            number_submitted += 1
