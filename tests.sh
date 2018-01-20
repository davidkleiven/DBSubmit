# Test script for the DBSubmit module

# Test the simplesubmit command
python bin/simplesubmit.py  --dbname=example.db --nproc=2 --workdir=./ --dbtable=runs

# Test the Cluster Expansion submit command
python bin/cesubmit.py --dbname=example.db --nproc=2 --workdir=./
