#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:55:59 2024

@author: Julien Masson
"""
if __name__=="__main__":

    import os
    import calendar
    import sys
    import optparse
    from EODAG_search import EODAG_search
    from create_yaml import create_yaml
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
    
    if len(sys.argv) == 1:
        prog = os.path.basename(sys.argv[0])
        print('      ' + sys.argv[0] + ' [options]')
        print("     Aide : ", prog, " --help")
        print("        ou : ", prog, " -h")
        sys.exit(-1)
    else:
        usage = "usage: %prog [options] "
        parser = OptionParser(usage=usage)
    
        parser.add_option("-y", "--year", dest="year", action="store", type="string",
                          help="year (int): Select year", default=None)
        parser.add_option("-m", "--month", dest="month", action="store", type="string",
                    help="Select month", default=None)
        parser.add_option("-d", "--download_path", dest="d_path", action="store", type="string",
                          help="download_path (str): Specify the path to store datas", default=None)
        parser.add_option("-s", "--service", dest="service", action="store", type="string",
                          help="service (str): For now, only 'peps' and 'theia' is supported", default='peps')
        parser.add_option("-p", "--product_type", dest="product_type", action="store", type="string",
                          help="productType (str): Type of data (check EODAG doc for more info", default="S2_MSI_L1C")
        parser.add_option("-t", "--tile_Identifier", dest="tile_Identifier", action="store", type="string",
                          help="tileIdentifier (str): Name of the tile that will be downloaded", default="48PWQ")
        parser.add_option("-c", "--credential", dest="credential", action="store", type="string",
                           help="Path to the credential for the download of selected product (.credential file)", default=None)
        parser.add_option("-l", "--local", dest="local", action="store", type="string",
                           help="Path to the local file where to store temporary files", default=None)
        (options, args) = parser.parse_args()
        
    print("Download path="+options.d_path)
    print("Local="+options.local)
    print("Year="+options.year)
    print("Month="+options.month)
    print("service="+options.service)
    print("Product_type="+options.product_type)
    print("Tile="+options.tile_Identifier)

    if options.year==None or options.tile_Identifier==None:
        raise ValueError("year,download_path or tileIdentifiers can't be empty")
        sys.exit()
    
    if options.month==None:
        starts=options.year+'-'+'01'+'-'+'01' #Start date
        ends=options.year+'-'+'12'+'-'+'31'   #end date
    else:
        if len(options.month)==1 :
            month='0'+options.month
        else:
            month=options.month
        starts=options.year+'-'+month+'-'+'01' #Start date
        ends=options.year+'-'+month+'-'+str(calendar.monthrange(int(options.year), int(options.month))[1]) #end date
        
    services=options.service.lower() #everything in lowercase
    

    #Setting download location ###########################################################################
    
    if options.local==None:
        if not os.path.isdir('eodag_workspace'):
            os.mkdir('eodag_workspace')
            os.chdir(os.path.join(os.getcwd(),'eodag_workspace'))
            dpath=os.getcwd()
    else :
        localp=options.local
    
    yaml_path=create_yaml(credential=options.credential,service=services,dpath=localp)
    src_path=os.path.join(localp,'Search_results')
    if not os.path.exists(src_path):
        os.mkdir(src_path)
    ###########################################################################
    
    setup_logging(2) #Startup logging
    dag = EODataAccessGateway(yaml_path)
    dag.set_preferred_provider(services) #What is the provider of datas
    
    Online,Offline=EODAG_search(download_path=localp,service=services,productTypes='S2_MSI_L1C',
                                tileIdentifiers=options.tile_Identifier,yaml_path=yaml_path,starts=starts,ends=ends)
    
    for i in range(0,len(Online)):
        Online[i].download()

    for i in range(0,len(Offline)):
        Offline[i].download(wait=2,timeout=30)

###########################################################################
    if options.month==None:
        
        Online_file = os.path.join(src_path, f"Online_{options.tile_Identifier}_{options.year}.geojson")
        Offline_file = os.path.join(src_path, f"Offline_{options.tile_Identifier}_{options.year}.geojson")
    else:
        Online_file = os.path.join(src_path, f"Online_{options.tile_Identifier}_{options.year}_{month}.geojson")
        Offline_file = os.path.join(src_path, f"Offline_{options.tile_Identifier}_{options.year}_{month}.geojson")
    
    dag.serialize(
        Online,
        filename=Online_file
    )
    
    dag.serialize(
        Offline,
        filename=Offline_file
    )
