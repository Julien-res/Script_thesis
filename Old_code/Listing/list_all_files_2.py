import os
import csv
import paramiko

os.chdir('C:\Travail\Script\Listing')
CSV_name='C:\Travail\Script\Listing\List_data\MREN\WiPE_RAW'

apath = '/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/WiPE/'
apattern = '"*.TIF"'
##PEPS
# locationdateS=-20
# locationdateE=-12
# locationnameS=-27
# locationnameE=-21

#WiPE
locationdateS=-25
locationdateE=-17
locationnameS=-32
locationnameE=-26

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
    date=filename[locationdateS:locationdateE]
    name=filename[locationnameS:locationnameE]
    Listd.append(date)
    Listn.append(name)
# ftp = ssh.open_sftp()
# for afile in filelist:
#     (head, filename) = os.path.split(afile)
#     print(filename)
#     ftp.get(bytes.decode(afile,'utf-8'), './'+bytes.decode(filename, 'utf-8'))
    
# ftp.close()
ssh.close()

with open(CSV_name+'.csv', 'w') as f:
    write=csv.writer(f,delimiter=';')
    for i in range(len (Listn)):
        write.writerow([Listd[i], Listn[i]])

        # write.writerow(lined)
        # write.writerow(linen)



