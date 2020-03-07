#!/bin/sh
dr=$(readlink $(dirname $0) )
if [ -n "$dr" ]; then cd $dr; fi
RUNDIR=/home/software/jhubcache
name=$RUNDIR/"$( mktemp )"
conffile=${name}.py
RUNDIR=$name
mkdir -p  $RUNDIR
chmod 1777 $RUNDIR






if ! [ -f jupyterhub_config.py ]; then 
   echo file not found
exit 1
fi
echo cp jupyterhub_config.py  $conffile
cp jupyterhub_config.py  $conffile


. /home/software/miniconda3/envs/jupyterhub//../../envs/jupyterhub/bin/envscript
#cd /tmp

# load anaconda if in non default location
#module load anaconda/3.7/jupyterhub
#in case spawner is in non default location
#export PYTHONPATH=$PYTHONPATH:/home/sean.brisbane/SLXSpawner
#needs to be writable to root and all users and shared


cd $RUNDIR

echo jupyterhub -f $conffile
jupyterhub -f $conffile 
