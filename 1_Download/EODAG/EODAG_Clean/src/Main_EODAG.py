#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:55:59 2024

@author: Julien Masson
"""
if not __name__ == "__main__":
    os.chdir ("/mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/EODAG_Clean/src/")
import os
import calendar
import argparse
from EODAG_search import EODAG_search
from create_yaml import create_yaml
from eodag import setup_logging
from eodag.api.core import EODataAccessGateway
from datetime import datetime
import glob
import re



def find_s2_files(directory, recursive=True):
    if directory is None:
        return None
    patterns = [f"S2{x}_MSIL1C_*.{ext}" for x in ["A", "B"] for ext in ["SAFE", "SAFE.bz2", "zip"]]
    matched_files = []
    for pattern in patterns:
        if recursive:
            matched_files.extend(
                glob.glob(os.path.join(directory, "**", pattern), recursive=True)
            )
        else:
            matched_files.extend(glob.glob(os.path.join(directory, pattern)))
    extracted = []
    mis = 0
    for fname in matched_files:
        match = re.search(r"_(\d{8})T.*?_T(\d+[A-Z]+)_", os.path.basename(fname))
        if match:
            if os.path.getsize(fname) / 1024 >= 50000:
                extracted.append((match.group(1), match.group(2)))
            else:
                if mis == 0:
                    print(f"At least one file is smaller than 50000KB and will be re-downloaded.")
                    mis = 1
    print('extracted: ', len(extracted), ' files extracted out of', len(matched_files))
    return extracted

def parse_arguments():
    parser = argparse.ArgumentParser(description="Download Sentinel-2 image")
    requiredNamed = parser.add_argument_group('Required Arguments')
    requiredNamed.add_argument("-y", "--year", type=int, dest='year', help="Year of the image", required=True)
    requiredNamed.add_argument("-t", "--tile", type=str, dest='tile', help="Desired tile(s) to download (e.g. 31TFJ)", nargs='+', required=True)
    requiredNamed.add_argument("-c", "--credential", type=str, dest='cred', help="Path to credential file (if no provider=>geodes)", required=True)
    parser.add_argument("-o", "--output", type=str, dest='output', help="Path where to output downloaded files (default: stdout)", default=None)
    parser.add_argument("-s", "--service", type=str, dest='serv', help="Provider where to download data", default='geodes')
    parser.add_argument("-m", "--month", type=int, dest='month', help="Month of the image")
    parser.add_argument("-k", "--check", type=str, dest='check', help="Optional path to check for already downloaded files", default=None)
    parser.add_argument("-r", "--recursive", dest='recursive', type=lambda x: (str(x).lower() == 'true'), help="Search subdirectories recursively (default: True)", default="true")
    return parser.parse_args()

def setup_download_path(output):
    if output is None:
        workspace = 'eodag_workspace'
        if not os.path.isdir(workspace):
            os.mkdir(workspace)
        return os.path.join(os.getcwd(), workspace)
    return output

def get_date_range(year, month):
    if month:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
        month_str = f"{month:02d}"
        start = f"{year}-{month_str}-01"
        end = f"{year}-{month_str}-{calendar.monthrange(year, month)[1]}"
    else:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
    return start, end

def filter_downloads(products, already_downloaded, tile):
    filtered = []
    for product in products:
        date_str = product.properties['startTimeFromAscendingNode'][:10].replace("-", "")
        cloud=product.properties['cloudCover']
        if (date_str, tile) not in already_downloaded:
            if cloud < 100:
                filtered.append(product)
                print(f"{date_str} {tile} to be downloaded")
            else:
                print(f"{date_str} {tile} cloud cover too high, Skipping.")
        else:
            print(f"{date_str} {tile} Already downloaded")
    return filtered

if __name__ == "__main__":
    print ('Launching')
    args = parse_arguments()
    if args.check:
        check = args.check
    else:
        check = args.output
    localp = setup_download_path(args.output)
    print(f'Local path: {localp}')
    print(f'Provider: {args.serv} (default: geodes)' if args.serv == 'geodes' else f'Provider: {args.serv}')
    print(f'Credential: {args.cred}')
    print(f'Tile: {args.tile}')
    print(f'Year: {args.year}')
    print(f'Month: {args.month}' if args.month else 'Month: not specified')
    print(f'Recursive: {args.recursive} (default: True)' if args.recursive else f'Recursive: {args.recursive}')
    print(f'Check: {args.check}' if args.check else 'Check: not specified')
    print(f'Output: {args.output}' if args.output else 'Output: not specified')
    print('Parsing arguments done')
    print('Searching for already downloaded files...')
    already_downloaded = find_s2_files(check, args.recursive)
    if not already_downloaded:
        print('No files found in the directory')
    else:
        print('{} found in the directory'.format(len(already_downloaded)))
    print('Starting EODAG...')
    yaml_path = create_yaml(credential=args.cred, service=args.serv, dpath=localp, totp=None)
    setup_logging(3)
    dag = EODataAccessGateway(yaml_path)
    dag.set_preferred_provider(args.serv)
    
    start, end = get_date_range(args.year, args.month)
    print(f'Start date: {start}')
    print(f'End date: {end}')
    
    for tile in args.tile:
        print(f'Processing tile {tile}')
        online, offline = EODAG_search(download_path=localp, service=args.serv, productType='S2_MSI_L1C', tileIdentifier=tile, yaml_path=yaml_path, start=start, end=end)
        
        if not online and not offline:
            print("Skipping current tile as no data is found.")
            continue
        
        online = filter_downloads(online, already_downloaded, tile)
        offline = filter_downloads(offline, already_downloaded, tile)
        
        if not online and not offline:
            print("Skipping current tile as all products were already downloaded.")
            continue
        
        if online or offline:
            print('At least one possible download')
            for i in range(0, len(online), 2):
                dag.download_all(online[i:i+1], wait=1, timeout=1, output_dir=localp)
                if len(online) < 2:
                    dag.download_all(online, wait=1, timeout=1, output_dir=localp)
            for i in range(0, len(offline), 2):
                dag.download_all(offline[i:i+1], wait=2, timeout=10, output_dir=localp)
                if len(offline) < 2:
                    dag.download_all(offline, wait=2, timeout=10, output_dir=localp)