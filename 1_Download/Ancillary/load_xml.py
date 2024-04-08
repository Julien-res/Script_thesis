# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 14:49:05 2024

@author: Julien Masson
"""
import os

def load_xml(path=None):
    import xml.etree.ElementTree as ET
    from datetime import datetime
    
    tree = ET.parse(os.path.join(path,'MTD_MSIL1C.xml'))
    for Sensing_time in tree.getroot().iter('DATATAKE_SENSING_START'):
        Output = datetime.strptime(Sensing_time.text, '%Y-%m-%dT%H:%M:%S.%fZ')
        return Output
