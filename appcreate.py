#!/usr/bin/env python
import sys, json, os, tempfile, stat, subprocess
from optparse import OptionParser
def getopts():
   parser = OptionParser()
   parser.add_option("-m", "--module", dest="appmodulename",
                     help="application module to add")
   parser.add_option("-a", "--appname", dest="appname",
                    help="application module to add")
   parser.add_option("-b", "--base", dest="basepath",
                     help="base environment path")
   parser.add_option("-c", "--conffile", dest="conffile",
                     help="Location of app config file",
                     default="/apps/jupyterhub/apps.json")

   (options, args) = parser.parse_args()
   return options, args
if __name__ == '__main__':
   (options, args) = getopts() 
   print (options)
   with open(options.conffile, "r") as conffile:
     apps = json.load(conffile)
   apps[options.appname] = options.appmodulename
   #fnamet =   tempfile.mkstemp()  
   fname="/tmp/tter"
   f=open(fname, "w")
   f.write("#!/bin/bash -l\nmodule load {0}; python -m ipykernel install --name={1} --prefix={2};\n".format(options.appmodulename, options.appname, options.basepath))
   f.close()
   os.chmod(fname, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE )
   p = subprocess.Popen(fname, stdout=subprocess.PIPE, shell=True)
   (output, err) = p.communicate()  
   p_status = p.wait()
   print (output, err)
   os.remove(fname)

