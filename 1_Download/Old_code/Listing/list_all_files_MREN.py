# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 15:06:04 2023

@author: Julien Masson
"""

import os
import csv
import paramiko

os.chdir('C:\Travail\Script\Listing')
CSV_name='C:\Travail\Script\Listing\List_data\MREN\Landsat\Landsat_LST'

apath = '/work/users/cverpoorter/VolTransMESKONG/VolTransMESKONG/Landsat/LST'
apattern = '"LC08_*_LST.tif"'

host='192.168.85.246'
username='mren'
password='Cambodge_0'
#%%=================================================================

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)


rawcommand = 'find {path} -name {pattern}'
command = rawcommand.format(path=apath, pattern=apattern)
stdin, stdout, stderr = ssh.exec_command(command)
filelist = stdout.read().splitlines()
Listd=[]
Listn=[]
for filepath in filelist:
    filename=bytes.decode(filepath,'utf-8')
    Listd.append(filename)

ssh.close()



with open(CSV_name+'.csv', 'w') as f:
    write=csv.writer(f,delimiter='\n')
    write.writerow(Listd)




