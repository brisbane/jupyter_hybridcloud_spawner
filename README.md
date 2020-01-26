# jupyter_hybridcloud_spawner

A spawner for batch system controlled environments initially as a mechanism to scale
python notebooks with batch and cloud facilities

## Requirements 
- jupyterhub with batchspawner installed
- working slurm queues at site
- If slurm not in sudoers secure path, it needs to be added
- A way to get jupyterhub on the path (eg module)

## Usage:
See examples for usage


## Instructions

An example environment set up is included to install dependencies using miniconda

#Configure applictions at 
/etc/jhcspawner/apps.json

creating apps is controlled by  appcreate.py
eg to create a second application that launhes into the default environment
/appcreate.py -m jupyterhub -a jupyterhub -b /root/miniconda3/envs/jupyterhub/ -d /home/software/modules

