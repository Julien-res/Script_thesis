#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:46:49 2024

@author: Julien Masson
"""

import os
import sys

def read_credentials(filename):
    try:
        with open(filename) as f:
            lines = [line.rstrip() for line in f]
            return [line.rstrip('\n') for line in lines]
    except Exception as e:
        print(f"Error reading .credential file: {e}")
        sys.exit(-2)

def write_yaml(yaml_path, yaml_content):
    with open(yaml_path, "w") as f_yml:
        f_yml.write(yaml_content.strip())
    os.chmod(yaml_path, 0o0600)

def create_yaml(credential=None, service='peps', dpath=None, totp=None):
    '''Create yaml needed to run EODAG specified parameters:
    
    Args:
        credential (str): Path where .credential files are stored. The default is None.
        service (str): Select service. The default is 'peps'.
        dpath (str): Path where to download EODAG output.
        totp (str): TOTP code from auth app (only for creodias).
    
    Returns:
        yaml_path (str): Path of the yaml created.
    '''
    if service == 'geodes':
        usrnm, passwd, apkey = read_credentials(os.path.join(credential, f"{service}.credential"))
        yaml_content = f"""
        {service}:
            download:
                outputs_prefix: '{dpath}'
                extract: false
                delete_archive: false
            auth:
                credentials:
                    username: {usrnm}
                    password: {passwd}
                    apikey: {apkey}
        """
    else:
        usrnm, passwd = read_credentials(os.path.join(credential, f"{service}.credential"))
        yaml_content = f"""
        {service}:
            download:
                outputs_prefix: '{dpath}'
                extract: true
                delete_archive: true
            auth:
                credentials:
                    username: {usrnm}
                    password: {passwd}
        """
        if service == 'creodias':
            yaml_content += f"        totp: {totp}"

    yaml_path = os.path.join(os.getcwd(), 'eodag_download_conf.yml')
    write_yaml(yaml_path, yaml_content)
    return yaml_path