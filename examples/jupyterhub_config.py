c = get_config()
c.NotebookApp.tornado_settings = {'headers': {'X-Frame-Options': 'ALLOW-FROM http://dublxmpv01'}}
c.JupyterHub.allow_named_servers = True
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.spawner_class = "CometSpawner.CometSpawner"
c.SlurmSpawner.cmd = "/apps/python/anaconda/el7/python3.7/2019.10/envs/singularity/bin/jupyterhub-singleuser"
import batchspawner 
c.SlurmSpawner.start_timeout = 7200
c.SlurmSpawner.startup_poll_interval = 5.0
c.SlurmSpawner.http_timeout = 7200
c.kernel_name = "geo"
cd $HOME
export PYTHONPATH="mytest:$PYTHONPATH"
module load anaconda/3.7/singularity
env
{cmd}
'''
{other}
cd $HOME
{cmd}
'''
c.SlurmSpawner.env_keep = ["PATH", "LD_LIBRARY_PATH"]
c.batchspawner.env_keep = ["PATH", "LD_LIBRARY_PATH"]
c.ProfilesSpawner.profiles = [
   ( "Local server", 'local', 'jupyterhub.spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
   ('Mesabi - 2 cores, 4 GB, 8 hours', 'mesabi2c4g12h', 'CometSpawner.CometSpawner',
      dict() ),
   ]
