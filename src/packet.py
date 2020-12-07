from collections import namedtuple 
from functools import partial 
from glob import glob
import logging 
from os.path import join 
from warnings import warn 
# TODO logging 

from pyshark import FileCapture as capture 
from pyshark.packet.packet import Packet as PKT
from tqdm import tqdm 

from constants import DATA_PATH

Packet = namedtuple('Packet', ['source', 'destination', 'timestamp'])

def parse_packet(packet: PKT): 
    try: 
        return Packet(packet['ip'].src, packet['ip'].dst, packet.sniff_timestamp)
    except KeyError as e: 
        # TODO logging 
        if 'ipv6' in (layer.layer_name for layer in packet.layers): 
            print('ipv6 packet detected... skipping') 
            return None 
        else: 
            print(e) 
            return None 

def load_traces(path: str = DATA_PATH) -> tuple: 
    pcap_paths, ts_paths = map(glob, map(partial(join, path), ['*.pcap', '*.times'])) 
    if len(pcap_paths) == 0: 
        warn(f'no pcap traces found... ensure a *.pcap file appears in {trace_path}')
    elif len(ts_paths) == 0: 
        warn(f'no timestamp file found... proceeding without timestamp correlation')
    elif len(pcap_paths) > 1: 
        warn(f'Found {len(pcap_paths)} pcap traces... using {pcap_paths[0]}')
    return (capture(pcap_paths[0]), ts_paths[0])

def parse_packet_stream(n_packets: int = 1, paths: tuple = None, **kwargs): 
    pcap_trace, ts_trace = load_traces() if paths is None else (capture(paths[0]), paths[1])
    packet_stream = () 
    n_loaded, errors = 0, 0
    for packet in tqdm(pcap_trace, disable=(not kwargs.get('verbose', False))): 
        if n_loaded == n_packets: break 
        parsed = parse_packet(packet)
        if parsed is not None: 
            packet_stream += (parsed,) 
            n_loaded += 1
        else: 
            errors += 1
    print(f"Loaded [{n_loaded}/{n_packets}] succesfully... {errors} loading errors") # TODO, logging 
    return packet_stream 

