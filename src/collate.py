import argparse 
import os 
import requests 
from urllib.parse import urlparse 

from constants import PCAP_TIMES_PATH, PCAP_STATS_PATH, PCAP_PATH, SRC_PATH 

parser = argparse.ArgumentParser() 
parser.add_argument('--all', type=bool, default=True)
parser.add_argument('--times', type=bool, default=False) 
parser.add_argument('--stats', type=bool, default=False) 
parser.add_argument('--trace', type=bool, default=False) 
parser.add_argument('-v', default=False, action='store_true', help='verbose mode')
args = parser.parse_args() 

if __name__=='__main__': 
    paths = [] 
    if args.times is True or args.stats is True or args.trace is True: 
        args.all = False 
        if args.times is True: 
            paths.append(PCAP_TIMES_PATH) 
        if args.stats is True: 
            paths.append(PCAP_STATS_PATH) 
        if args.trace is True: 
            paths.append(PCAP_PATH) 
    else: 
        paths.append(PCAP_PATH, PCAP_STATS_PATH, PCAP_TIMES_PATH) 

    try: 
        caida_usr, caida_key = map(os.environ.get, ['CAIDA_USR', 'CAIDA_KEY'])
    except: 
        print('Ensure environment variables CAIDA_USR, CAIDA_KEY are set') 

    data_dir_path = os.path.join(SRC_PATH, "data")
    if not os.path.exists(data_dir_path): 
        if args.v: print("Data directory not found, creating {data_dir_path}") 
        os.makedirs(data_dir_path) 

    for url in paths: 
        if args.v: print(f"Loading from url {url}...")
        fname = os.path.basename(urlparse(url).path)
        output_fname = os.path.join(data_dir_path, fname) 
        r = requests.get(url, auth=(caida_usr, caida_key))
        if r.status_code == 200 and args.v: 
            print(f"Success... writing to output {output_fname}")
        else: 
            print(f"Request failure with status code {r.status_code}")

        with open(output_fname, 'wb') as out: 
            out.write(r.content) 

