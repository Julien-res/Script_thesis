# -*- coding: utf-8 -*-
"""
@author: Julien Masson
"""

import os
import calendar
import sys
import optparse
import pip

try:
    __import__('eodag')
except ImportError:
    pip.main(['install', 'eodag'])   
             
from eodag import setup_logging
from eodag.api.core import EODataAccessGateway

###########################################################################

class OptionParser (optparse.OptionParser):

    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)
            
###########################################################################
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print('      ' + sys.argv[0] + ' [options]')
    print("     Aide : ", prog, " --help")
    print("        ou : ", prog, " -h")
    # print("example 1 : python %s -l 'Toulouse' -a peps.txt -d 2016-12-06 -f 2017-02-01 -c S2ST" % sys.argv[0])
    # print("example 2 : python %s --lon 1 --lat 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2" % sys.argv[0])
    # print("example 3 : python %s --lonmin 1 --lonmax 2 --latmin 43 --latmax 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2" %
    #       sys.argv[0])
    # print("example 4 : python %s -l 'Toulouse' -a peps.txt -c SpotWorldHeritage -p SPOT4 -d 2005-11-01 -f 2006-12-01" %
    #       sys.argv[0])
    # print("example 5 : python %s -c S1 -p GRD -l 'Toulouse' -a peps.txt -d 2015-11-01 -f 2015-12-01" % sys.argv[0])
    sys.exit(-1)
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)

    parser.add_option("-y", "--year", dest="year", action="store", type="string",
                      help="year (int): Select year", default=None)
    parser.add_option("-m", "--month", dest="month", action="store", type="string",
                      help="month (int): Select month (format:2 numbers)",default=None)
    parser.add_option("-d", "--download_path", dest="d_path", action="store", type="string",
                      help="download_path (str): Specify the path to store datas (will auto-create year and month files required)", default='.')
    parser.add_option("-s", "--service", dest="service", action="store", type="string",
                      help="service (str): For now, only 'peps' and 'theia' is supported", default='peps')
    parser.add_option("-p", "--product_type", dest="product_type", action="store", type="string",
                      help="productType (str): Type of data (check EODAG doc for more info", default="S2_MSI_L1C")
    parser.add_option("-t", "--tile_Identifier", dest="tile_Identifier", action="store", type="string",
                      help="tileIdentifier (str): Name of the tile that will be downloaded", default="48PWQ")
     parser.add_option("-c", "--credential", dest="credential", action="store", type="string",
                       help="Path to the credential for the download of selected product (.credential file)", default=None)
    (options, args) = parser.parse_args()
    
# try:
#     f = open(options.credential)
#     (email, passwd) = f.readline().split(' ')
#     if passwd.endswith('\n'):
#         passwd = passwd[:-1]
#     f.close()
# except:
#     print("error with password file")
#     sys.exit(-2)

###########################################################################

def EODAG_boot(year=None,month=None,download_path=None,service='peps',productTypes='S2_MSI_L1C',tileIdentifiers=None,geom=None,**kwargs):
    '''Run EODAG with specified parameters
    Args:
        year (str): Select year (DUH...).
        month (str): Select month.
        download_path (str): Specify the path to store datas (will auto-create year and month files required).
        service (str): For now, only 'peps', 'theia' and 'landsat' is supported.
        productType (str): Type of data (check EODAG doc for more info https://eodag.readthedocs.io/en/latest/notebooks/api_user_guide/2_providers_products_available.html or check Test_EODAG.py.
        tileIdentifier (str): Name of the tile that will be downloaded
        
    '''

    if year==None or month==None or download_path==None or tileIdentifiers==None:
        raise ValueError("year, month,download_path or tileIdentifiers can't be empty")
        sys.exit()
    starts=year+'-'+month+'-'+'01' #Start date
    ends=year+'-'+month+'-'+str(calendar.monthrange(int(year), int(month))[1]) #end date
    if len(month)==1 :
        month='0'+month
        
    setup_logging(2) #Startup logging
    service=service.lower() #everything in lowercase
    
    
    
    #Setting download location ###########################################################################
    
    if download_path==None:
        if not os.path.isdir('eodag_workspace'):
            os.mkdir('eodag_workspace')
            os.chdir(os.path.join(os.getcwd(),'eodag_workspace'))
    else :
        os.chdir(download_path) 
            
    if not os.path.exists(os.path.join(format(os.getcwd()),year)): #create year and month files if they dont exist
       os.mkdir(year)
    os.chdir(download_path+'/'+year)
    if not os.path.exists(os.path.join(format(os.getcwd()),month)):
       os.mkdir(month)
    os.chdir(download_path+'/'+year+'/'+month)
    
    services=service.lower()+':'
    
    # Setting up credential ###########################################################################


    filename=os.path.join(options.credential,(service+'.credential'))
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
        
    # Save the PEPS configuration file. ###########################################################################
    yaml_content = services+"""
        download:
            outputs_prefix: '{}'
            extract: true
            delete_archive: true
        auth:
            credentials:
                username: XXX
                password: YYY
    """.format(os.getcwd()).replace('XXX',lines[0]).replace('YYY',lines[1])
    
    with open(os.path.join(format(os.getcwd()), 'eodag_conf_{}.yml'.format(service)), "w") as f_yml:
        f_yml.write(yaml_content.strip())
    
    
    dag = EODataAccessGateway(os.path.join(format(os.getcwd()), 'eodag_conf_{}.yml'.format(service)))
    dag.set_preferred_provider(service) #What is the provider of datas
    
    #Search in Service database ###########################################################################
    products = dag.search_all(
        productType=productTypes,
        start=starts,
        end=ends,
        tileIdentifier=tileIdentifiers
    )
    
    online_search_results = products.filter_property(storageStatus="ONLINE")
    offline_search_results = products.filter_property(storageStatus="OFFLINE")
    
    #download to location ###########################################################################
    #Download online Product
    if len(online_search_results)<2:
        dag.download_all(online_search_results)
    else:
        for i in range(0,len(online_search_results),2):
            if i<len(products):
                dag.download_all(online_search_results[i:i+1])
            else:
                online_search_results[i].download()
    
    #Download try to download Product 
         
    if len(offline_search_results)<2:
        dag.download_all(offline_search_results,wait=1,timeout=10)
    else:
        for i in range(0,len(offline_search_results),2):
            if i<len(products):
                dag.download_all(offline_search_results[i:i+1],wait=1,timeout=10)
            else:
                offline_search_results[i].download(wait=1,timeout=10)
                
                
                
EODAG_boot(year=options.year,month=options.month,download_path=options.d_path,service=options.service,productTypes=options.product_type,tileIdentifiers=options.tile_Identifier)