# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 10:03:01 2023

@author: Julien Masson
"""
import os
import re
import sys
import glob
import optparse
import datetime
import subprocess
import shapely
import pip
import shapely.wkt
try:
    __import__('pandas')
except ImportError:
    pip.main(['install', 'pandas'])
import pandas as pd
try:
    __import__('eodag')
except ImportError:
    pip.main(['install', 'eodag'])
from eodag import setup_logging
from eodag.api.core import EODataAccessGateway

PTH=os.getcwd()
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

    parser.add_option("-e", "--Entry", dest="entry", action="store", type="string",
                      help="Entry (str): Path to csv of already downloaded datas"
                      ,default=None)
    parser.add_option("-l", "--Compared", dest="cmpr", action="store", type="string",
                      help="Compared (str): Path to files with all csv of online datas"
                      ,default=None)
    parser.add_option("-d", "--download_path", dest="dpath", action="store", type="string",
                      help="download_path (str): Specify the path to download missing datas"
                      ,default='.')
    parser.add_option("-s", "--service", dest="svc", action="store", type="string",
                      help="service (str): For now, only 'peps', 'theia','landsat' and 'earth_search_gcs' is supported"
                      ,default='peps')
    parser.add_option("-p", "--product_type", dest="product_type", action="store", type="string",
                      help="productType (str): Type of data (check EODAG doc for more info"
                      ,default="S2_MSI_L1C")
    parser.add_option("-c", "--credential", dest="credential", action="store", type="string",
               help="Path to the credential for the download of selected product (.credential file)", default=None)
    (options, args) = parser.parse_args()

# Setting up credential #################################################
filename=os.path.join(options.credential,(service+'.credential'))
with open(filename) as file:
    lines = [line.rstrip() for line in file]

# Save the PEPS configuration file. ###############################################

services=options.svc.lower()+':'
yaml_path=os.path.join(format(os.getcwd()), f'eodag_download_conf_{services}_.yml')

setup_logging(2) #Startup logging
yaml_content = services+f"""
    download:
        outputs_prefix: '{options.dpath}'
        extract: true
        delete_archive: true
    auth:
        credentials:
            username: {lines[0]}
            password: {lines[1]}
"""
with open(yaml_path, "w") as f_yml:
    f_yml.write(yaml_content.strip())
os.chmod(yaml_path, 0o0600)

dag = EODataAccessGateway(yaml_path)
dag.set_preferred_provider(services) #What is the provider of datas

# Dictionary to retrieve tiles location. ###########################################################################
dictt={'48PWQ':'MULTIPOLYGON(((104.999818016115 9.04674336507645,104.999818486685 8.05356904776694,105.9962750648 8.05235960109292,105.998857367364 9.04538249198545,104.999818016115 9.04674336507645)))',
       '48PWR':'MULTIPOLYGON(((104.999817537813 9.95140803202204,104.999818060333 8.95828239172743,105.998614716536 8.95693503733834,106.001482101143 9.94990852813499,104.999817537813 9.95140803202204)))',
       '48PXR':'MULTIPOLYGON(((105.91227099375 9.95016377400518,105.909658942959 8.95716438436966,106.908183437359 8.95336310801134,106.913659569089 9.94593324618135,105.91227099375 9.95016377400518)))',
       '48PWS':'MULTIPOLYGON(((104.999817011879 10.8554812215646,104.999817586985 9.86240892564619,106.001212263618 9.86092309166698,106.004368205585 10.8538424370562,104.999817011879 10.8554812215646)))',
       '48PXS':'MULTIPOLYGON(((105.914900098204 10.8541213912038,105.912025184585 9.86117601065097,106.913144234408 9.85698404894791,106.91917142632 10.8494979199674,105.914900098204 10.8541213912038)))',
       '48PYS':'MULTIPOLYGON(((106.829191450726 10.850045783753,106.823446450796 9.85748078107257,107.824027824035 9.85058955962639,107.832916841275 10.8424452222986,106.829191450726 10.850045783753)))',
       '48PVT':'MULTIPOLYGON(((104.081859097617 11.7585667054579,104.085001970386 10.7656801799762,105.089272013709 10.7670169065032,105.089578700793 11.7600299650333,104.081859097617 11.7585667054579)))',
       '48PWT':'MULTIPOLYGON(((104.99981643701 11.7600440278082,104.999817065469 10.7670297532165,106.004074129854 10.7654046301732,106.007522844522 11.7582650725709,104.99981643701 11.7600440278082)))',
       '48PXT':'MULTIPOLYGON(((105.917773825769 11.7585678864829,105.914632209105 10.7656812588743,106.918609804219 10.7610963297671,106.925196098882 11.7535489624956,105.917773825769 11.7585678864829)))',
       '48PYT':'MULTIPOLYGON(((106.834934052968 11.7541436852337,106.828656123509 10.761639626516,107.832088553437 10.7541024225341,107.841802069159 11.7458930622207,106.834934052968 11.7541436852337)))',
       '48PVU':'MULTIPOLYGON(((104.078737295539 12.662955140335,104.08215103359 11.6701320236949,105.089550213142 11.6715839785989,105.08988333229 12.6645344210406,104.078737295539 12.662955140335)))',
       '48PWU':'MULTIPOLYGON(((104.999815812764 12.6645495988525,104.999816495387 11.6715979327288,106.00720249948 11.6698327211119,106.010948436823 12.6626295912909,104.999815812764 12.6645495988525)))',
       '48PXU':'MULTIPOLYGON(((105.920894380166 12.6629564150023,105.917482006473 11.6701331955956,106.924584311107 11.6651530453262,106.931738198272 12.6575395531398,105.920894380166 12.6629564150023)))',
       '48PUV':'MULTIPOLYGON(((103.151727696596 13.5616096529548,103.159097669413 12.5692421659068,104.169633143047 12.5742798525896,104.166306971195 13.5670592145354,103.151727696596 13.5616096529548)))',
       '48PVV':'MULTIPOLYGON(((104.999815138748 13.5684512783988,104.99981587639 12.5755667024232,106.010599286693 12.5736606128775,106.014647134957 13.5663893456211,104.999815138748 13.5684512783988)))',
       '48PWV':'MULTIPOLYGON(((104.999815138748 13.5684512783988,104.99981587639 12.5755667024232,106.010599286693 12.5736606128775,106.014647134957 13.5663893456211,104.999815138748 13.5684512783988)))',
       '48PXV':'MULTIPOLYGON(((105.924263722465 13.5667403276824,105.920576320674 12.5739850674781,106.931071402892 12.5686074711303,106.938801826385 13.5609230675797,105.924263722465 13.5667403276824)))',
       '48PWA':'MULTIPOLYGON(((104.999814413269 14.4728301295702,104.99981520693 13.4800171375689,106.014272984892 13.4779691350645,106.018628231441 14.4706251494433,104.999814413269 14.4728301295702)))',
       '48PWB':'MULTIPOLYGON(((104.999813635756 15.3771395871771,104.999814486486 14.384402561123,106.018226451696 14.3822116162345,106.022894858562 15.3747904412497,104.999813635756 15.3771395871771)))',
       '48PXQ':'MULTIPOLYGON(((105.909879986275 9.04561414016698,105.907527632251 8.05256547349456,106.903715151216 8.04915327056808,106.908646852945 9.04177472412182,105.909879986275 9.04561414016698)))',
       '48PYQ':'MULTIPOLYGON(((106.819159638289 9.04222968127125,106.8144588429 8.04955760486627,107.810121485316 8.04394821135626,107.817394952377 9.03591799933518,106.819159638289 9.04222968127125)))',
       '48PYR':'MULTIPOLYGON(((106.823937657461 9.94643454820023,106.818717920098 8.95381354578377,107.816711490993 8.94756456080819,107.824787852301 9.93947992928979,106.823937657461 9.94643454820023)))',
       '31UCS':'MULTIPOLYGON(((0.123708231717921 51.4158835889695,0.183927395114058 50.4297129911636,1.72930089180216 50.4568611701362,1.70209212718467 51.4439979075417,0.123708231717921 51.4158835889695)))',
       '31UDS':'MULTIPOLYGON(((1.56054785010055 51.4423452524337,1.59072158561628 50.4552653391189,3.1375124947572 50.463717167285,3.14045795769041 51.451098077765,1.56054785010055 51.4423452524337)))',
       '31UES':'MULTIPOLYGON(((2.99971217585129 51.4511822052998,2.99971821166917 50.4637984012643,4.54643644145313 50.4535232784269,4.57954402145941 51.440541165328,2.99971217585129 51.4511822052998)))',
       '31UDT':'MULTIPOLYGON(((1.53152890259821 52.3413478023562,1.56330512055076 51.3544323478999,3.14018879864347 51.36315784254,3.14329076675524 52.3503862832372,1.53152890259821 52.3413478023562)))',
       '31UCR':'MULTIPOLYGON(((0.178667516435534 50.5181000379823,0.235902710263617 49.5317312072946,1.75278304384606 49.5580339519242,1.72692441603779 50.5453331581444,0.178667516435534 50.5181000379823)))',
       '31UDR':'MULTIPOLYGON(((1.58808613663728 50.5437323313927,1.61676273286422 49.5564878429428,3.13497050262122 49.5646762973658,3.13776975576675 50.5522106217701,1.58808613663728 50.5437323313927)))',
       '31UER':'MULTIPOLYGON(((2.99971768449213 50.5522921101345,2.99972342069688 49.5647549995183,4.51786312753597 49.5548000567925,4.54932814672628 50.5419848175809,2.99971768449213 50.5522921101345)))',
       '31UCQ':'MULTIPOLYGON(((0.230932063003636 49.6195968744803,0.285371051812801 48.633031814836,1.77513103779737 48.6585189158972,1.7505374049727 49.6459809660565,0.230932063003636 49.6195968744803)))',
       '31UDQ':'MULTIPOLYGON(((1.61427236819387 49.644430072972,1.64154622508782 48.6570207745726,3.1325513271229 48.6649551513509,3.13521359578014 49.6526438682633,1.61427236819387 49.644430072972)))',
       '31UEQ':'MULTIPOLYGON(((2.99972292255259 49.6527228140172,2.99972837804882 48.6650314110799,4.4906696405144 48.6553853482852,4.52059565371614 49.6427370646749,2.99972292255259 49.6527228140172)))'
       }

path=options.cmpr

all_files =[]

# Load all .csv with online data list ################################################

for filename in glob.glob(f'{path}/**/{services}_*_data.csv', recursive=True):
    all_files.append(filename)
Listd=[]
Listn=[]
Listo=[]
All=pd.DataFrame()
for f in all_files:
    dft=pd.read_csv(f,delimiter=';',index_col=False)
    Listd=Listd+dft['Date'].values.tolist()
    Listn=Listn+dft['Tile'].values.tolist()
    Listo=Listn+dft['Online'].values.tolist()

d = {'Date': Listd,'Tile': Listn}
Alrdonl=pd.DataFrame(data=d)
Alrdonl['Date']=pd.to_datetime(Alrdonl['Date'],format='%Y%m%d',yearfirst=True)


df_out=Alrdonl.groupby(['Date'])['Tile'].value_counts().unstack().fillna(0).astype(int).reindex()
df_out = df_out.groupby(pd.Grouper(freq="M"))
df_out=df_out.sum()
df_out.to_csv(path_or_buf=os.path.join(path,f'All_data_disp_{services}_bymonth.csv')
              ,sep=';',date_format='%Y%m%d')

# Load already downloaded data #############################################

Alrd=pd.read_csv(os.path.join(options.entry,(services+'.csv'))
                ,delimiter=';',index_col=False,header=None)

# Process data in order to be used to compare ################################

Listd=[]
Listn=[]
for t in Alrd.iloc[:,0].values:
    Listd.append(re.search(r'\d{8}', t).group())
    if re.search(r'Landsat', t) is not None:
        Listn.append(re.search(r'(?<=_)\d{6}(?=_)', t).group())
    else:
        Listn.append(re.search(r'\d{2}[A-Z]{3}', t).group())

d = {'Date': Listd,'Tile': Listn}
dft=pd.DataFrame(data=d)
date=pd.to_datetime(dft.iloc[:,0],format='%Y%m%d',yearfirst=True)
data={'Tile':dft.iloc[:,1],'Date':date}
df=pd.DataFrame(data)

# Output difference between online disp and already downloaded (what is in file is what need to be downloaded)
df3 = pd.merge(Alrdonl, df, how='outer', indicator='Exist')
df3 = df3[df3.Exist != 'both']
df3 = df3[df3.Exist != 'right_only']
test4=df3
test4=test4.drop('Exist',axis=1)
test4=test4.reset_index(drop=True)

test4.to_csv(path_or_buf=os.path.join(path,f'Missing_data_{services}_bymonth.csv')
             ,sep=';',date_format='%Y%m%d',index=False)

#Search in Service database ####################################

if services in ('peps','theia'):
    for i in range(0,len(test4)):
        starts=str(test4['Date'][i]-pd.DateOffset(1))[0:10]
        ends=str(test4['Date'][i]+pd.DateOffset(1))[0:10]
        tileIdentifiers=test4['Tile'][i]
        if i==0:
            products= dag.search_all(
                productType=options.product_type,
                start=starts,
                end=ends,
                tileIdentifier=tileIdentifiers
            )
        else:
            dum= dag.search_all(
                productType=options.product_type,
                start=starts,
                end=ends,
                tileIdentifier=tileIdentifiers
            )
            products=products+dum
            
elif services=='earth_search_gcs':
    for i in range(0,len(test4)):
        starts=str(test4['Date'][i]-pd.DateOffset(1))[0:10]
        ends=str(test4['Date'][i]+pd.DateOffset(1))[0:10]
        tileIdentifiers=test4['Tile'][i]
        if i==0:
            products= dag.search_all(
                productType=options.product_type,
                start=starts,
                end=ends,
                geom=dictt(tileIdentifiers)
            )
        else:
            dum= dag.search_all(
                productType=options.product_type,
                start=starts,
                end=ends,
                geom=shapely.wkt.loads(dictt[tileIdentifiers]).centroid.wkt
            )
            products=products+dum

online_search_results = products.filter_property(storageStatus="ONLINE")
offline_search_results = products.filter_property(storageStatus="OFFLINE")

#download to location ###########################################################################

os.chdir(options.dpath)
#Download online Product
if len(online_search_results)<2:
    dag.download_all(online_search_results)
else:
    for i in range(0,len(online_search_results),2):
        if i<len(products):
            dag.download_all(online_search_results[i:i+1])
        else:
            online_search_results[i].download()

#Try to download Offline Product

if len(offline_search_results)<2:
    dag.download_all(offline_search_results,wait=1,timeout=20)
else:
    for i in range(0,len(offline_search_results),2):
        if i<len(products):
            dag.download_all(offline_search_results[i:i+1],wait=1,timeout=20)
        else:
            offline_search_results[i].download(wait=1,timeout=20)

# Reprocess what have been downloaded ##############################################################
subprocess.call(['sh', os.path.join(PTH,f'find_{services}_data.sh')])
