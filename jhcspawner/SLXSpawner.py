import os
from batchspawner import SlurmSpawner
#from oauthenticator.cilogon import CILogonSpawnerMixin
from traitlets import Unicode
import json

class HybridCloudSpawner(SlurmSpawner):

    req_gres = Unicode('', config=True, \
        help="Additional resources requested"
        )

    def _options_form_default(self):
        appopts=""
        #TODO read these in from cluser config file
        default_apps= { 
                 "singularity": "singularity",
                 "tensorflow": "anaconda/tensorflow"
              }
        #print (self.appsconfig)
        appsconfig = "/etc/jhcspawner/apps.json"

        try:
           f=open(appsconfig,"r")
           apps = json.load(f)
        except: 
           print ("cannot load apps definition from {}, using default apps".format(appsconfig))
           apps = default_apps
        
        for i in apps.keys():
           appopts+=" <option value=\"{0}\">{1}</option>".format( apps[i], i) 
        """Create a form for the user to choose the configuration for the SLURM job"""
        return """
        <label for="queue">Node type</label>
        <select name="queue">
          <option value="debug">headnode</option>
          <option value="azurecpu">Cloud CPU node</option>
          <option value="azuregpu">Cloud GPU node</option>
        </select>
        <label for="gpus">Number of GPUs (only for shared GPU node)</label>
        <select name="gpus">
          <option value="0">0</option>
          <option value="1">1</option>
        </select>
        <label for="cores">Number of cores (only for cpu nodes)</label>
        <select name="cores">
          <option value="1">1</option>
          <option value="6">6</option>
        </select>
        <label for="nodes">Number of nodes</label>
        <select name="nodes">
          <option value="1">1</option>
          <option value="2">2</option>
        </select>
        <label for="runtime">Job duration</label>
        <select name="runtime">
          <option value="1:00:00">1 hour</option>
          <option value="2:00:00">2 hours</option>
          <option value="5:00:00">5 hours</option>
          <option value="8:00:00">8 hours</option>
          <option value="12:00:00">12 hours</option>
          <option value="24:00:00">24 hours</option>
        </select>
        <label for="application">Application</label>
        <select name="application">
          {0}
        </select>
        <label for="environment">Furhter environment settings and preparatory commandsto run</label>
        <textarea name="environment" rows="4" cols="50">
        </textarea>
        """.format(appopts)

    def options_from_form(self, formdata):
        """Parse the form and add options to the SLURM job script"""
        options = {}
        options['queue'] = formdata.get('queue', [''])[0].strip()
        options['runtime'] = formdata.get('runtime', [''])[0].strip()
        options['other'] = ''
        account = formdata.get('account', [''])[0].strip()
        if account:
            options['other'] += "#SBATCH --account={}".format(account)
        if options['queue'].startswith('gpu'):
            options['other'] += "\n#SBATCH --gres='gpu:{}'".format(formdata.get("gpus")[0])
        options['other'] += "\n#SBATCH --ntasks-per-node={}".format(formdata.get("cores")[0])
        options['other'] += "\n#SBATCH --nodes={}".format(formdata.get("nodes")[0])
        options['other'] += "\nmodule load {}".format(formdata.get("application")[0])
        options['other'] += "\n{}".format(formdata.get("environment")[0])
        print (options)
        return options

