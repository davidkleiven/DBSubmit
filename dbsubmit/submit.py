import datetime
import subprocess

class Submit(object):
    def __init__( self, arguments ):
        self.args = arguments
        self.scriptnames = []
        self.runIds = []

    def getJobIDs( self ):
        raise NotImplementedError("This is specific to the application and has to be implemented in child classes")

    def updateDB( self, jobID ):
        raise NotImplementedError("This is specific to the application and has to be implemented in child classes")

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
                of.write( "mpirun -np %d %s %s %d\n"%(self.args["nodes"]*self.args["nproc"], self.args["command"], self.args["main"], runID) )

    def submit( self ):
        self.generate()
        for script,runID in zip(self.scriptnames,self.runIds):
            #subprocess.call( ["qsub", script] )
            self.updateDB( runID )
