#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 10:49:52 2024

@author: Julien Masson
"""

# -*- coding: utf-8 -*-
"""
@author: Julien Masson
"""


def EODAG_search(download_path=None,service='peps',productTypes='S2_MSI_L1C',tileIdentifiers=None,yaml_path=None,starts=None,ends=None,**kwargs):
    '''Run EODAG with specified parameters
    Args:
        download_path (str): Specify the path to store datas (will auto-create year and month files required).
        service (str): For now, only 'peps', 'theia' and 'landsat' is supported.
        productType (str): Type of data (check EODAG doc for more info https://eodag.readthedocs.io/en/latest/notebooks/api_user_guide/2_providers_products_available.html or check Test_EODAG.py.
        tileIdentifier (str): Name of the tile that will be downloaded
        starts (str) : Start date to search data from. Format :YYYY-mm-dd
        ends (str) : end date to search data from. Format :YYYY-mm-dd
    '''
    import pip
    try:
        __import__('eodag')
    except ImportError:
        pip.main(['install', 'eodag'])    
    from eodag import setup_logging
    from eodag.api.core import EODataAccessGateway
    
    setup_logging(2) #Startup logging
    dag = EODataAccessGateway(yaml_path)
    dag.set_preferred_provider(service) #What is the provider of datas

    products = dag.search_all(
        productType=productTypes,
        start=starts,
        end=ends,
        tileIdentifier=tileIdentifiers
    )
    
    online_search_results = products.filter_property(storageStatus="ONLINE")
    offline_search_results = products.filter_property(storageStatus="OFFLINE")

    return (online_search_results,offline_search_results)