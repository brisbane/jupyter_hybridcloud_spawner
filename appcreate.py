#!/usr/bin/env python3
import sys, json, os, tempfile, stat, subprocess
from optparse import OptionParser
from shutil import copy
import errno

#example to create an app from the conda environment /home/software/miniconda3/envs/tensorflow2.1/
#appcreate  -e conda/tensorflow-2.1 -n tensorflow2.1 -b /home/software/miniconda3/envs/tensorflow2.1/ -t conda -d /home/software/modules/
#example to create a singluarity application - the sinularity app needs the default entrypoint script set up to run jupyterhub-singleuser
#appcreate  -e /home/software/containers/tensorflow-leap.sif  -n tensorflow2.1-singularity  -t singularity
#example singularity where you want to run a setup script first, inside the container, to configure the environment - the setup script should be acessible on a nfs share
#appcreate  -e /home/software/containers/tensorflow-leap.sif  -n tensorflow2.1-singularity  -t singularity -b /home/software/containers/tensorflow-leap-entry.sh


def getopts():
   parser = OptionParser()
   parser.add_option("-e", "--environment", dest="environmentname",
                     help="application module name or singularity image to use)")
   parser.add_option("-n", "--appname", dest="appname",
                    help="name for application in jupyter to add")
   parser.add_option("-b", "--base", dest="basepath",
                     help="base environment path for module based apps, or environment preps script (on host system) for singularity)")
   parser.add_option("-c", "--conffile", dest="conffile",
                     help="Location of app config file",
                     default="/etc/jhcspawner/apps.json")
   parser.add_option("-d", "--modulebaselocation", dest="modulebaselocation",
                     default="/usr/share/modules",
                     help="Location of modulesfiles (ignored for singularity)")
   parser.add_option("-t", "--type", dest="apptype",
                     default="conda",
                     help="Application type [=conda,singularity]")
   (options, args) = parser.parse_args()
   return options, args
if __name__ == '__main__':
    (options, args) = getopts() 
    print (options)
    if not os.path.exists(options.conffile):
       #print ("Failed to locate configuration file %s" % options.conffile)
       if not os.path.exists( os.path.dirname(options.conffile) ):
             os.mkdir( os.path.dirname(options.conffile) )
       apps={}
    else:
       try:
          with open(options.conffile, "r") as conffile:
             apps = json.load(conffile)
       except:
          print ("apps config file exists but might be corrupt")
          sys.exit(1)
    apps[options.appname] = {'name': options.appname, 'environmentname': options.environmentname, 'apptype': options.apptype }
  


    subenv=options.appname
    if 'singularity' == options.apptype:
        if options.basepath and options.basepath != "":
           apps[options.appname]['container_external_envprep']  = options.basepath
    if 'conda' == options.apptype:
      basenvissubenv=True

      if basenvissubenv:
         relpath="/../.."
      else:
         relpath=''
      baseenv=options.basepath+relpath
    
      scripttmp="/tmp/{0}-condainit-{1}".format(os.environ['USER'], subenv)
      moduletmp="/tmp/{0}-module-{1}".format(os.environ['USER'], subenv)

      moduledest="{0}/{1}".format(options.modulebaselocation, options.environmentname)
      scriptdest="{0}/envs/{1}/bin/envscript".format(baseenv, subenv)

      try:
         os.makedirs(os.path.dirname(scriptdest))

      except OSError as e : 
           if e.errno != errno.EEXIST:
                 raise
      try:
         os.makedirs(os.path.dirname(moduledest))
      except OSError as e : 
           if e.errno != errno.EEXIST:
                 raise
       
      baseenvv=os.path.realpath(baseenv)
      scriptdest="{0}/envs/{1}/bin/envscript".format(baseenv, subenv)

      f=open(scripttmp,"w")

      stri='''
# >>> conda initialize >>>
__conda_setup=$("{0}/bin/conda" 'shell.bash' 'hook' 2> /dev/null)
if [ $? -eq 0 ]; then
  eval "$__conda_setup"
else
  if [ -f "{0}/envs/{1}/etc/profile.d/conda.sh" ]; then
      . "{0}/envs/{1}/etc/profile.d/conda.sh"
  else
      export PATH="{0}/envs/{1}/bin:$PATH"
  fi
fi
unset __conda_setup
# <<< conda initialize <<<
conda activate --stack {0}/envs/{1}
      '''.format(baseenv, subenv)
      f.write(stri)
      f.close()

      f=open(moduletmp,"w")

      stri='''#%Module 1.0
if [info exists env(ORIG_PYTHONPATH)] {
    unsetenv PYTHONPATH $env(ORIG_PYTHONPATH)
    # Set the ORIG_PYTHONPATH inside this if clase so its unset during an unload
    setenv ORIG_PYTHONPATH $env(ORIG_PYTHONPATH)
} else {
    unsetenv PYTHONPATH
}

if [info exists env(PYTHONPATH)] {
    setenv ORIG_PYTHONPATH $env(PYTHONPATH)
}
'''
      stri+='puts stdout "source {0}"\n'.format(scriptdest)
      f.write(stri)
      f.close()

      copy(scripttmp, scriptdest)
      copy(moduletmp, moduledest)


      #fnamet =   tempfile.mkstemp()  
      fname="/tmp/conda-tmp-{}".format(os.environ['USER'])
      f=open(fname, "w")
      f.write("#!/bin/bash -l\necho 'testing the module {0} is working'\nmodule load {0}; python -m ipykernel install --name={1} --prefix={2};\n".format(options.environmentname, options.appname, options.basepath))
      f.close()
      os.chmod(fname, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE )
      p = subprocess.Popen(fname, stdout=subprocess.PIPE, shell=True)
      (output, err) = p.communicate()  
      p_status = p.wait()
      print (str(output), str(err))
      #os.remove(fname)

    print ("Finalizing by adding the application")
    json.dump(apps,open(options.conffile,"w"))
