import os
from batchspawner import SlurmSpawner
#from oauthenticator.cilogon import CILogonSpawnerMixin
from traitlets import Unicode
import json

class HybridCloudSpawner(SlurmSpawner):

    req_gres = Unicode('', config=True, \
        help="Additional resources requested"
        ).tag(config=True)
    req_site_environment = Unicode('', config=True, \
        help="Additional environment settings for site"
        ).tag(config=True)
    req_schedoptions = Unicode('', \
        help="Other options to include into job submission script"
        ).tag(config=True)

#Overriden by the form options
    SlurmSpawner.batch_script = Unicode("""#!/bin/bash
#SBATCH --partition={partition}
#SBATCH --time={runtime}
#SBATCH --output={homedir}/jupyterhub_slurmspawner_%j.log
#SBATCH --job-name=spawner-jupyterhub
#SBATCH --mem={memory}
#SBATCH --export={keepvars}
#SBATCH {schedoptions}
. /usr/share/Modules/3.2.10/init/bash
{site_environment}
cd $HOME
{other}
{cmd}
""").tag(config=True)

    appsconfig = Unicode("/etc/jhcspawner/apps.json").tag(config=True)
    
    def loadapps(self):
         

        #TODO read these in from cluser config file
        default_apps= {
                 "jupyterhub":  { 'environmentname': "conda/jupyterhub", 'apptype': "conda" },
                 "singularity-tensorflow": { 'environmentname': "/home/software/containers/jupyter-notebook-suse.simg", 'apptype': "singularity"},
                 "tensorflow":  { 'environmentname': "conda/tensorflow", 'apptype': "conda" },
                 "tensorflow-gpu":  { 'environmentname': "conda/tensorflow-gpu", 'apptype': "conda" }
              }
        #print (self.appsconfig)
        appsconfig=self.appsconfig

        try:
           f=open(appsconfig,"r")
           apps = json.load(f)
        except:
           print ("cannot load apps definition from {}, using default apps".format(appsconfig))
           apps = default_apps
        return apps

    def _options_form_default(self):
        appopts=""
        apps = self.loadapps()
        for i in apps.keys():
           appopts+=" <option value=\"{0}\">{1}</option>".format( apps[i]['environmentname'], i) 
        """Create a form for the user to choose the configuration for the SLURM job"""
        return """
        <br/>
        <table>
         <tr>
            <td align="left"><label for="queue">Node type</label></td>
            <td align="right">
            <select name="queue">
              <option value="debug">headnode</option>
              <option value="azurecpu">Cloud CPU node</option>
              <option value="azuregpu">Cloud GPU node</option>
            </select>
            </td>
        </tr>
        <tr>
          <td align="left"><label for="runtime">Job duration</label></td>
          <td align="right">
          <select name="runtime">
            <option value="1:00:00">1 hour</option>
            <option value="2:00:00">2 hours</option>
            <option value="5:00:00">5 hours</option>
            <option value="8:00:00">8 hours</option>
            <option value="12:00:00">12 hours</option>
            <option value="24:00:00">24 hours</option>
          </select>
          </td>
        </tr>
        <tr>
          <td align="left">
          <label for="application">Application</label>
          </td>
          <td align="right">
          <select name="application">
          {0}
          </select>
          </td>
        </tr>
        </table>
        <!---<div id="advanced" class="collapse">--->
        <tr>
          <td align="left"><label for="nodes">Number of nodes</label></td>
          <td align="right">
          <select name="nodes">
            <option value="1">1</option>
            <option value="2">2</option>
          </select>
          </td>
          <td align="right">
          <label for="cores">Number of cores</label>
          </td>
          <td align="right">
          <select name="cores">
            <option value="1">1</option>
            <option value="6">6</option>
          </td>
          </select>
          <td align="right">
          <label for="gpus">Number of GPUs</label>
          <select name="gpus">
            <option value="0">0</option>
            <option value="1">1</option>
          </select>
          </td>
        </tr>
        <br/>
        <label for="environment">Further environment settings and preparatory commands to run</label>
        <textarea name="environment" rows="4" cols="50">
        </textarea><br/>
        <!---</div>
        <table><tr><td align="left"><img src="https://securelinx.com/wp-content/themes/wp-slx-v4/img/logo.png"></td>-->
        </tr></table>
        """.format(appopts)

    def options_from_form(self, formdata):
        """Parse the form and add options to the SLURM job script"""
        apps = self.loadapps()
        options = {}
        options['queue'] = formdata.get('queue', [''])[0].strip()
        options['runtime'] = formdata.get('runtime', [''])[0].strip()
        print (options)
        options['schedoptions'] = ''
        options['keep_vars'] = ""
        options['other'] = """
env
cd $HOME
"""
#.format(options['queue'], options['runtime'])
        application = formdata.get("application")[0]
        for app in apps:
            print ( app )
            if apps[app]['environmentname'] == application: 
                apptype = apps[app]['apptype']  
                print (apptype + " found")  
                break
 
        account = formdata.get('account', [''])[0].strip()
        if account:
            options['schedoptions'] += "#scheduler"
            options['schedoptions'] += "#SBATCH --account={}".format(account)
        if options['queue'].startswith('azuregpu'):
            options['schedoptions'] += "\n#SBATCH --gres=gpu:{}".format(formdata.get("gpus")[0])
        options['schedoptions'] += "\n#SBATCH --ntasks-per-node={}".format(formdata.get("cores")[0])
        options['schedoptions'] += "\n#SBATCH --nodes={}".format(formdata.get("nodes")[0])
        options['other'] += "\n{}".format(formdata.get("environment")[0])
        if  apptype  != "singularity":
            options['other'] += "\nmodule load {}".format(formdata.get("application")[0])

        else:
            options['other'] += "\nexport LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
            options['other'] += "\nexport SINGULARITY_LD_LIBRARY_PATH=/usr/local/cuda/lib64"
            options['other'] += "\nexport SINGULARITY_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
            options['other'] += "\nsingularity exec --nv {} \\".format(apps[app]['environmentname'])
        self.batch_script = """#!/bin/bash
#SBATCH --partition={0}
#SBATCH --time={1}
#SBATCH --output=jupyterhub_slurmspawner_%j.log
#SBATCH --job-name=spawner-jupyterhub
""".format(options['queue'], options['runtime'] )
#.tag(config=True)
        self.batch_script += "\n{schedoptions}"

        self.batch_script += "\n. /usr/share/Modules/3.2.10/init/bash"
        self.batch_script += '\n' + self.req_site_environment
        self.batch_script += options['other']
        self.batch_script += "\n{cmd}"
        return options

