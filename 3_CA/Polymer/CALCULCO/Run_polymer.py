#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import optparse
from glob import glob
from polymer.main import run_atm_corr
from polymer.level2_nc import Level2_NETCDF
from polymer.level1_msi import Level1_MSI
from polymer.ancillary import Ancillary_NASA


###########################################################################
class OptionParser (optparse.OptionParser):
    '''Parse options'''
    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error(f"{option} option not supplied")
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print('      ' + sys.argv[0] + ' [options]')
    print("     Aide : ", prog, " --help")
    print("        ou : ", prog, " -h")
    sys.exit(-1)
else:
    USAGE = "usage: %prog [options] "
    parser = OptionParser(usage=USAGE)

    parser.add_option("-i", "--input", dest="input_file", action="store", type="string",
                      help="input (str): path of input datas (MSI-L1C)", 
                      default=None)
    parser.add_option("-o", "--output", dest="output_file", action="store", type="string",
                      help="output (str): Path where output datas",
                      default=None)
    parser.add_option("-a", "--ancillary", dest="ancillary_file", action="store", type="string",
                      help="output (str): Path where ancillary datas are stored",
                      default=None)
    parser.add_option("-r", "--resolution", dest="reso", action="store", type="string",
                      help="output (str): Desired output resolution",
                      default=None)
    (options, args) = parser.parse_args()


######### Define number of Threads ############


def polymer(imfolder,savename):
    print(f"\n Processing {savename} ...\n")
    run_atm_corr(Level1_MSI(imfolder, resolution = options.reso,
        ancillary=Ancillary_NASA(directory=options.ancillary_file)),
        Level2_NETCDF(savename,overwrite=True),multiprocessing=-1)

    print(f"\n Processing {savename} Done! ...\n")

######### Run Polymer correction ############
if __name__ == '__main__':
    
    ######### Define image directory ############
    
    Input=options.input_file
    Output=options.output_file
    
    if Output is None:
        if not os.path.isdir('Polymer_workspace'):
            os.mkdir('Polymer_workspace')
            os.chdir(os.path.join(os.getcwd(),'Polymer_workspace'))
            Output=os.path.join(os.getcwd(),'Polymer_workspace')
    else :
        os.chdir(Output)
    listimfolder=glob(Input+'/GRANULE/'+'L1C*')
    savename=os.path.join(Output,(listimfolder[0]'_polymer'+options.reso+'m.nc'))
    polymer(Input,savename)  
