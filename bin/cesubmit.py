#!/usr/bin/env python
import sys
from dbsubmit.commandParser import CommandLineArgParser
from dbsubmit.specificSubmitters import ASE

def main( argv ):
    parser = CommandLineArgParser( argv )
    submitter =ASEClusterExpansionSubmit( parser.arguments )
    submitter.submit()

if __name__ == "__main__":
    main( sys.argv[1:] )
