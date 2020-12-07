from collections import namedtuple # TODO yeah yeah 
from glob import glob 
import os 
import sys 
from warnings import warn

import pyshark 
from pyshark import FileCapture as capture
from tqdm import tqdm 

from constants import DATA_PATH

Packet = namedtuple('Packet', ['source', 'destination', 'timestamp'])
PKT = pyshark.packet.packet.Packet

def parse_packet(x: PKT, **kwargs): 
    src, dst, ts = x['ip'].src, x['ip'].dst, x.sniff_timestamp # TODO: want this as a str or something else 
    return Packet(src, dst, ts) 

def load_packet_stream(n_packets: int = 1, ts_range: tuple = None, path: str = DATA_PATH, **kwargs): 
    try:
        pcap_paths, ts_paths = glob(os.path.join(path, '*.pcap')), glob(os.path.join(path, '*.times'))
        if len(pcap_paths) == 0: 
            warn(f'pcap trace not found... please check that a [*.pcap] file appears in {path}') 
            sys.exit()
        elif len(ts_paths) == 0:
            warn(f'pcap timestamps file not found... proceeding without timestamp correlation') 
        if len(pcap_paths) > 1: 
            warn(f'multiple pcap traces found... using {pcap_paths[0]} for packet stream loading') 
        trace = capture(pcap_paths[0]) 
        packet_stream = () 
        loaded = 0
        for packet in tqdm(trace, disable=(not kwargs.get('verbose', False))): 
            if loaded == n_packets: 
                break 
            packet_stream += (parse_packet(packet),)
            loaded += 1 
    except Exception as e: 
        print(e) 
    return packet_stream 

def phash(key):
    # Hashes an arbitrary key to a random value between 0 and 1.
    # Could probably be made cleaner.
    v = hash(str(key))
    return (v % 2**16) / 2**16

def count(arr):
    # Counts the number of true boolean values in an array.
    return sum(arr)

def flip_coin():
    # Flips a random coin.
    # It would be nice to make this deterministic but pseudorandom,
    # so that our code has no truly random components.
    return bool(random.randint(0,1))

def table_size(table):
    total = 0
    for k in table:
        total += len(table)
    return total
