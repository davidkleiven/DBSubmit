from dbsubmit.submit import Submit
import sqlite3 as sq

class SimpleStatusFieldSubmit(Submit):
    def __init__( self, args ):
        Submit.__init__(self, args )

        self.states = {
            "newJob":"new",
            "qeuedJob":"submitted",
            "finishedJob":"finished"
        }

    def getJobIDs( self ):
        """
        Returns all job IDs of the new jobs
        """
        con = sq.connect( self.args["dbname"] )
        cur = con.cursor()
        cur.execute( "SELECT ID FROM %s WHERE status='%s'"%( self.args["dbtable"], self.states["newJob"],) )
        ids = cur.fetchall()
        con.close()

        idlist = [entry[0] for entry in ids]
        return idlist

    def updateDB( self, jobID ):
        """
        Updates the DB to set the job as submitted
        """
        con = sq.connect( self.args["dbname"] )
        cur = con.cursor()
        cur.execute( 'UPDATE %s SET status="%s" WHERE ID=?'%(self.args["dbtable"], self.states["qeuedJob"],), (jobID,))
        con.commit()
        con.close()

try:
    import ase.db
    hasASE = True
except ImportError:
    hasASE = False

class ASEClusterExpansionSubmit(Submit):
    """line
    Class that submits jobs susing ASE database in a similar way as the included Submit class
    https://gitlab.com/jinchang/ase/blob/ClusterExpansion/ase/ce/job.py
    """
    def __init__( self, args ):
        Submit.__init__( self, args)

    def getJobIDs( self ):
        """
        Returns all the job IDs
        """
        if ( not hasASE ):
            raise ImportError("Could not find ASE")

        db = ase.db.connect( self.args["dbname"] )
        if ( "restart" in self.args.keys() ):
            # Re-start an old simulation that was not converged
            condition = "converged=False"
        else:
            # Run a new simulation
            condition = "queued=False, started=False"
        ids = [row.id for row in db.select(condition)]
        return ids

    def updateDB( self, id ):
        """
        Sets the queued flag to True
        """
        if ( not hasASE ):
            raise ImportError("Could not find ASE")
        db = ase.db.connect( self.args["dbname"] )
        db.update( id, queued=True )
