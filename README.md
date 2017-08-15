# DBSubmit
Submit script for jobs stored in a database.
The scripts creates a job script similar to the one found [here](https://www.hpc.ntnu.no/display/hpc/Tutorial+for+submitting+parallel+job+to+VILJE+with+Code+Saturne).

The script makes a few assumption about the SQL-database and the GPAW script
1) There is a field in the database named ID which contains a unique job ID (has to be an integer)
2) There is a field in the database named STATUS
3) The GPAW scripts takes a the ID as a command line argument

There are two ways of passing command line arguments described in [here](gpawsubmit.py).

The script submittes all jobs that has status *new* and sets the STATUS field to *submitted*.
It is a good idea to let the GPAW script setts the STATUS field to for instance *finished* when the job is finished.
