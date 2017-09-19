import sys
from dbsubmit.commandParser import CommandLineArgParser
from dbsubmit.specificSubmitters import SimpleStatusFieldSubmit

def main( argv ):
    parser = CommandLineArgParser( argv )
    submitter = SimpleStatusFieldSubmit( parser.arguments )
    submitter.submit()

if __name__ == "__main__":
    main( sys.argv[1:] )
