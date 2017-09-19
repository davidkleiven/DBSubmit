
class CommandLineArgParser(object):
    def __init__( self, argv ):
        """
        Initialize the parser

        Parameters:
        argv: The sys.arg[1:] array
        """
        self.argv = argv
        self.arguments = {
            "projID":None,
            "name":"noname",
            "walltime":"00:00:00",
            "nodes":1,
            "nproc":1,
            "dbname":None,
            "dbtable":"notUsed",
            "workdir":None,
            "main":None,
            "command":"python"
        }

        self._parse()
        self._checkRequired()

    def _parse( self ):
        """
        Parse the command line arguments
        """
        for arg in self.argv:
            if ( arg.find("--projID=") != -1 ):
                self.arguments["projID"] = arg.split( "--projID=" )[1]
            elif ( arg.find("--name=") != -1 ):
                self.arguments["name"] = arg.split("--name=" )[1]
            elif ( arg.find("--walltime=") != -1 ):
                self.arguments["walltime"] = arg.split("--walltime=" )[1]
            elif ( arg.find("--nodes=") != -1 ):
                self.arguments["nodes"] = int( arg.split( "--nodes=" )[1] )
            elif ( arg.find("--nproc=") != -1 ):
                self.arguments["nproc"] = int( arg.split( "--nproc=" )[1] )
            elif ( arg.find("--dbname") != -1 ):
                self.arguments["dbname"] = arg.split( "--dbname=" )[1]
            elif ( arg.find("--dbtable=") != -1 ):
                self.arguments["dbtable"] = arg.split( "--dbtable=" )[1]
            elif ( arg.find("--workdir") != -1 ):
                self.arguments["workdir"] = arg.split("--workdir=")[1]
            elif ( arg.find("--main=") != -1 ):
                self.arguments["main"] = arg.split("--main=")[1]
            elif ( arg.find("--command=") != -1 ):
                self.arguments["command"] = arg.split("--command=")[1]
            elif ( arg.find("-h") or arg.find("--help") ):
                print ("Required arguments:")
                print (self.arguments)
                exit()

    def _checkRequired( self ):
        """
        Check that all the required arguments are given
        """
        if ( self.arguments["workdir"] is None ):
            raise ValueError("Working directory not given!")
        if ( self.arguments["dbname"] is None ):
            raise ValueError("Database not given!")
