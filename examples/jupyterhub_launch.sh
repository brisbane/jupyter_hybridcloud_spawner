#!/bin/sh
cd $(dirname $0)

conffile="$( mktemp ).py"

if ! [ -f jupyterhub_config.py ]; then 
   echo file not found
exit 1
fi
cp jupyterhub_config.py  $conffile
cd /tmp

module load conda/jupyterhub

# load anaconda if in non default location
#module load anaconda/3.7/jupyterhub
#in case spawner is in non default location
#export PYTHONPATH=$PYTHONPATH:/home/sean.brisbane/SLXSpawner


echo jupyterhub -f $conffile
jupyterhub -f $conffile
