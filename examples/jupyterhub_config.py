c = get_config()
c.JupyterHub.allow_named_servers = True
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.spawner_class = "SLXSpawner.HybridCloudSpawner"
#import batchspawner
#call the full path to this or load a module to ensure it is on the path
c.SlurmSpawner.cmd = "jupyterhub-singleuser"

c.SlurmSpawner.batch_script = '''#!/bin/bash
#SBATCH --job-name="jupyterhub"
#SBATCH --output="jupyterhub.%j.%N.out"
#SBATCH --partition={queue}
#SBATCH --nodes=1
#SBATCH --time={runtime}
#SBATCH --get-user-env=L

###### Output generated from HybridCloudSpawner
{other}
########
cd $HOME
{cmd}
'''


c.SlurmSpawner.start_timeout = 7200
c.SlurmSpawner.startup_poll_interval = 5.0
c.SlurmSpawner.http_timeout = 7200
