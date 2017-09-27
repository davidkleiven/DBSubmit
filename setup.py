from setuptools import setup

setup(
    name="dbsubmit",
    version=1.0,
    author="David Kleiven",
    atuhor_email="davidkleiven446@gmail.com",
    description="Scripts for submitting jobs to a cluster where input parameters are stored in a SQL database",
    packages=["dbsubmit"],
    scripts=["bin/cesubmit.py","bin/simplesubmit.py"]
)
