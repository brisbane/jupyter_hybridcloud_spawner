import os
from batchspawner import SlurmSpawner
#from oauthenticator.cilogon import CILogonSpawnerMixin
from traitlets import Unicode
import json

class HybridCloudSpawner(SlurmSpawner):

    req_gres = Unicode('', config=True, \
        help="Additional resources requested"
        )
    
    def loadapps(self):
         

        #TODO read these in from cluser config file
        default_apps= {
                 "singularity-tensorflow": { 'environmentname': "/home/software/containers/jupyter-tensorflow-notebool.simg", 'apptype': "singularity"},
                 "tensorflow":  { 'environmentname': "conda/tensorflow", 'apptype': "conda" }
              }
        #print (self.appsconfig)
        appsconfig = "/etc/jhcspawner/apps.json"

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
        options['other'] = """
#SBATCH --job-name="jupyterhub"
#SBATCH --output="jupyterhub.%j.%N.out"
#SBATCH --partition={queue}
#SBATCH --nodes=1
#SBATCH --time={runtime}
#SBATCH --get-user-env=L

cd $HOME
"""
        application = formdata.get("application")[0]
        for app in apps:
            print ( app )
            if apps[app]['environmentname'] == application: 
                apptype = apps[app]['apptype']  
                print (apptype + " found")  
                break
 
        account = formdata.get('account', [''])[0].strip()
        if account:
            options['other'] += "#SBATCH --account={}".format(account)
        if options['queue'].startswith('azuregpu'):
            options['other'] += "\n#SBATCH --gres='gpu:{}'".format(formdata.get("gpus")[0])
        options['other'] += "\n#SBATCH --ntasks-per-node={}".format(formdata.get("cores")[0])
        options['other'] += "\n#SBATCH --nodes={}".format(formdata.get("nodes")[0])
        if  apptype  != "singularity":
            options['other'] += "\nmodule load {}".format(formdata.get("application")[0])
            options['other'] += "\n{}".format(formdata.get("environment")[0])
        else:
            options['other'] += "\nsingularity run -B /etc/group:/etc/group -B /etc/passwd:/etc/passwd -B /home:/home {} \\".format(apps[app]['environmentname'])
        print (options)
        return options

