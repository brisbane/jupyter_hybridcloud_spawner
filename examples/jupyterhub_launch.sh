#!/bin/sh
cd /tmp
#in case spawner is in non default location
#export PYTHONPATH=$PYTHONPATH:/home/conda/SLXSpawner
# load anaconda if in non default location
#module load anaconda/base
jupyterhub -f ./jupyterhub_config.py

