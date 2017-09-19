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
