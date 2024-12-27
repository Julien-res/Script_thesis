#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:46:49 2024

@author: Julien Masson
"""

def create_yaml(credential=None,service='peps',dpath=None,totp=None):
    '''Create yaml needed to run EODAG specified parameters:
    
Args:
    credential (str), Needed
            Path wgere .credential files are stored. The default is None.
    service (str), optional:
            Select service . The default is 'peps'
    dpath (str), Needed
            Path where to download EODAG output
    totp (str), optional
            TOTP code from auth app (only for creodias)
Returns:
    yaml_path (str)
            Path of the yaml created
    None.

    '''
    import os
    import sys
    ###############################################
    if service=='geodes':
        filename=os.path.join(credential,(service+'.credential'))
        try:
            with open(filename) as f:
                lines = [line.rstrip() for line in f]
                usrnm=lines[0]
                passwd=lines[1]
                apkey=lines[2]
                if usrnm.endswith('\n'):
                    usrnm = usrnm[:-1]
                if passwd.endswith('\n'):
                    passwd = passwd[:-1]
                if apkey.endswith('\n'):
                    apkey = apkey[:-1]
        except:
            print("Error with .credential file, check if you made it right boss!")
            sys.exit(-2)

        # Save the PEPS configuration file. ###############################################
        yaml_path=os.path.join(format(os.getcwd()), 'eodag_download_conf.yml')
        yaml_content = service+':'+f"""
        download:
            outputs_prefix: '{dpath}'
            extract: true
            delete_archive: true
        auth:
            credentials:
                username: {usrnm}
                password: {passwd}
                apikey: {apkey}
        """
        with open(yaml_path, "a") as f_yml:
            yaml_content=yaml_content+f"""        totp: {totp}"""
            f_yml.write('\n')
            f_yml.write(yaml_content.strip())
        os.chmod(yaml_path, 0o0600)
        return yaml_path
    else:
        filename=os.path.join(credential,(service+'.credential'))
        try:
            with open(filename) as f:
                lines = [line.rstrip() for line in f]
                usrnm=lines[0]
                passwd=lines[1]
                if usrnm.endswith('\n'):
                    usrnm = usrnm[:-1]
                if passwd.endswith('\n'):
                    passwd = passwd[:-1]
        except:
            print("Error with .credential file, check if you made it right boss!")
            sys.exit(-2)

        # Save the PEPS configuration file. ###############################################
        yaml_path=os.path.join(format(os.getcwd()), 'eodag_download_conf.yml')
        yaml_content = service+':'+f"""
        download:
            outputs_prefix: '{dpath}'
            extract: true
            delete_archive: true
        auth:
            credentials:
                username: {usrnm}
                password: {passwd}
        """
        if service != 'creodias':
            with open(yaml_path, "w") as f_yml:
                f_yml.write(yaml_content.strip())
            os.chmod(yaml_path, 0o0600)
        else :

            with open(yaml_path, "a") as f_yml:
                yaml_content=yaml_content+f"""        totp: {totp}"""
                f_yml.write('\n')
                f_yml.write(yaml_content.strip())
            os.chmod(yaml_path, 0o0600)
        return yaml_path