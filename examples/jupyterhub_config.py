c = get_config()
c.JupyterHub.allow_named_servers = True
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.spawner_class = "jhcspawner.SLXSpawner.HybridCloudSpawner"
#call the full path to this or load a module to ensure it is on the path
#c.SlurmSpawner.cmd = "jupyterhub-singleuser --debug"
c.HybridCloudSpawner.req_site_environment = "source /etc/profile.d/custommodulepath.sh"
#c.JupyterHub.BaseHandler.slow_spawn_timeout = 60
c.Spawner.debug = True
c.HybridCloudSpawner.start_timeout = 7200
c.HybridCloudSpawner.startup_poll_interval = 5.0
c.HybridCloudSpawner.http_timeout = 7200
