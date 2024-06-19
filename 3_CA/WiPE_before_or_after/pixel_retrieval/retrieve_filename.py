"""Module containing all commands that output a list of files to process"""
import glob
def POLYMER(tile,path):
    """Return all Polymer files contained in path"""
    allpath=glob.glob(path+'L1C_'+tile+'*polymer20m.nc')
    return allpath

def WiPE(tile,path):
    """Return all WiPE files contained in path"""
    allpath=glob.glob(path+'S2*_'+tile+'*_water.TIF')
    return allpath
