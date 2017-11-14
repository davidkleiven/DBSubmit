# Configuration script
import sys

settings_file = "dbsubmit/settings.py"

def check_args( args, accepted_args ):
    for key,value in args.iteritems():
        if ( not value in accepted_args[key] ):
            raise ValueError("Unknown argument found")

def generate_settings_file( args ):
    with open(settings_file, 'a') as of:
        for key,valyue in args.iteritems():
            of.write("{}={}\n".format(key,value))
    print ("Configuration options written to %s"%(settings_file))

def main( argv ):
    accepted_args = {
    "cluster":["stallo","vilje"]
    }

    args = {
        "cluster":"vilje"
    }

    for arg in argv:
        if ( arg.find("--help") != -1 ):
            print ("Arguments:")
            print (args)
            return
    elif ( arg.find("--cluster=") != -1 ):
        args["cluster"] = arg.split("--cluster=")[1]

    check_args( args, accepted_args )
    generate_settings_file(args)

if __name__ == "__main__":
    main( sys.argv[1:] )
