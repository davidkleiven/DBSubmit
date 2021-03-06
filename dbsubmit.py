import sys
import subprocess
import sqlite3 as sq
import random as rnd
import json
import datetime

def main( argv ):
    """
    This script creates submit scripts for all jobs in a database where the field status is 'new'
    The job is submitted to the cluster and the status field is changed to 'submitted'

    All the arguments in the 'arguments' dictionary below should be given.
    Put -- in front of each name and = after (with no whitespaces)

    Example:
    python dbsubmit.py --projID=nn1204ub --name=myjob --walltime=01:12:01 --nodes=2 --nproc=16
    --dbname=/path/to/sql/database.db --dbtable=parameters --workdir=/path/to/where/outputfiles
    --main=/path/to/the/gpaw/script.py --command=python

    Alternatively the paramters can be read from a json file.
    This is useful if you are using the same paramters for many runs

    Example:
    python dbsubmit.py --file=params.json

    An example of such file can be found in params.json

    Parameters:
    -------------
    projID: ID of the project where there are availabe CPU time
    name: Name of the job
    walltime: Estimated wall time (think the job is aborted if the run time exeeds this)
    nodes: Number of nodes
    nproc: Number of processes
    dbname: Name of the database where the parameters are stored
    dbtable: Table in the database where the parameters are stored
    workdir: Working directory. The submit script and the output files will be put here
    main: GPAW script to run
    command: Executable command, default: python, for GPAW it should be gpaw-python

    NOTE: The database should have a field named status and one named ID
          The IDs will be passed as command line argument to the GPAW script
          The ID field should have datatype INT
    """
    arguments = {
        "projID":None,
        "name":"noname",
        "walltime":"00:00:00",
        "nodes":1,
        "nproc":1,
        "dbname":None,
        "dbtable":None,
        "workdir":None,
        "main":None,
        "command":"python"
    }

    if ( len(argv) == 1 and argv[0].find("--file=") != -1 ):
        # Read parameters from file
        fname = argv[0].split("--file=")[1]
        with open( fname, 'r' ) as infile:
            arguments = json.load( infile )
    else:
        for arg in argv:
            if ( arg.find("--projID=") != -1 ):
                arguments["projID"] = arg.split( "--projID=" )[1]
            elif ( arg.find("--name=") != -1 ):
                arguments["name"] = arg.split("--name=" )[1]
            elif ( arg.find("--walltime=") != -1 ):
                arguments["walltime"] = arg.split("--walltime=" )[1]
            elif ( arg.find("--nodes=") != -1 ):
                arguments["nodes"] = int( arg.split( "--nodes=" )[1] )
            elif ( arg.find("--nproc=") != -1 ):
                arguments["nproc"] = int( arg.split( "--nproc=" )[1] )
            elif ( arg.find("--dbname") != -1 ):
                arguments["dbname"] = arg.split( "--dbname=" )[1]
            elif ( arg.find("--dbtable=") != -1 ):
                arguments["dbtable"] = arg.split( "--dbtable=" )[1]
            elif ( arg.find("--workdir") != -1 ):
                arguments["workdir"] = arg.split("--workdir=")[1]
            elif ( arg.find("--main=") != -1 ):
                arguments["main"] = arg.split("--main=")[1]
            elif ( arg.find("--command=") != -1 ):
                arguments["command"] = arg.split("--command=")[1]
            elif ( arg.find("-h") or arg.find("--help") ):
                print ("Required arguments:")
                print (arguments)
                return

    # Create the submission script
    if ( arguments["workdir"] is None ):
        print ( "Working directory not given!" )
        print ( "Required arguments:" )
        print ( arguments )
        return

    if ( arguments["dbname"] is None ):
        print ("No database given!")
        return
    if ( arguments["dbtable"] is None ):
        print ("No table in database given!")
        return

    con = sq.connect( arguments["dbname"] )
    cur = con.cursor()
    cur.execute( "SELECT ID FROM %s WHERE status='new'"%(arguments["dbtable"]) )
    ids = cur.fetchall()
    con.close()

    timestamp = datetime.datetime.today().strftime( "%Y%m%d_%H%M%S")
    for i in range(len(ids)):
        runID = int( ids[i][0] )
        scriptname = arguments["workdir"]+"/job_%s_%d.sh"%(timestamp,i)
        with open(scriptname, 'w') as of:
            of.write("#!/bin/bash\n")
            of.write("#PBS -N %s\n"%(arguments["name"]) )
            of.write("#PBS -l walltime=%s\n"%(arguments["walltime"]) )
            of.write("#PBS -l select=%d:ncpus=32:mpiprocs=%d\n"%(arguments["nodes"],arguments["nproc"]) )
            of.write("#PBS -A %s\n"%(arguments["projID"]) )

            # Export paths
            of.write("module load intelcomp/17.0.0 mpt/2.14\n")
            of.write("module load python/2.7.13\n")
            of.write('export LD_LIBRARY_PATH="/usr/lib64":"/home/ntnu/davidkl/.local/lib":${LD_LIBRARY_PATH}\n')
            of.write('export GPAW_SETUP_PATH="/home/ntnu/davidkl/GPAW/gpawData/gpaw-setups-0.9.20000"\n')
            of.write('export PATH=${PATH}:"/home/ntnu/davidkl/.local/bin"\n')
            of.write('export PYTHONPATH=${PYTHONPATH}:"/home/ntnu/davidkl/.local/lib/python2.7/site-packages/ase-3.15.0b1-py2.7.egg"\n')
            of.write('export PYTHONPATH=${PYTHONPATH}:"/home/ntnu/davidkl/.local/lib/python2.7/site-packages/"\n')
            of.write( "cd %s\n"%(arguments["workdir"]) )
            of.write( "mpirun -np %d %s %s %d\n"%(arguments["nodes"]*arguments["nproc"], arguments["command"], arguments["main"], runID) )

        subprocess.call( ["qsub", scriptname] )
        con = sq.connect( arguments["dbname"] )
        cur = con.cursor()
        cur.execute( 'UPDATE %s SET status="submitted" WHERE ID=?'%(arguments["dbtable"]), (runID,))
        con.commit()
        con.close()

if __name__ == "__main__":
    main( sys.argv[1:] )
