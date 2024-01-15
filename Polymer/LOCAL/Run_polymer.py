#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import optparse
import threading
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
    parser.add_option("-f", "--format", dest="fmt", action="store", type="string",
                      help="format (str): specify the output data format (Optional)",
                      default='autodetect')
    (options, args) = parser.parse_args()


######### Define number of Threads ############
MAXTHREADS = 1 # Threads count for downloads
sema = threading.Semaphore(value=MAXTHREADS)
threads = []

def polymer(imfolder,savename):
    sema.acquire()
    try:
        if os.path.isfile(savename):
            sema.release()
        else:  
            print(f"\n Processing {savename} ...\n")
            run_atm_corr(Level1_MSI(imfolder, resolution = '20',
                                    ancillary=Ancillary_NASA(directory=options.ancillary_file)),
                         Level2_NETCDF(savename,fmt='.nc',overwrite=True),
                         multiprocessing=-1)
            sema.release()
        print(f"\n Processing {savename} Done! ...\n")
    except ValueError:
        raise("\n Multithreading error! ...\n")
        Runpolymer(threads, imfolder,savename)

def Runpolymer(threads, imfolder,savename):
    thread = threading.Thread(target=polymer, args=(imfolder,savename,))
    threads.append(thread)
    thread.start()
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

    imfolder=glob(Input+'/GRANULE/'+'L1C*')
    folder_name = os.path.basename(imfolder)
    savename=os.path.join(format(Output),f'/{folder_name}_polymer20m.nc')
    Runpolymer(threads, imfolder,savename)  
