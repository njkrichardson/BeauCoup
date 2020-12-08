from collections import namedtuple 
from functools import partial 
from glob import glob
import logging 
from os.path import join 
from warnings import warn 

from pyshark import FileCapture as capture 
from pyshark.packet.packet import Packet as PKT
from tqdm import tqdm 

from constants import DATA_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
try: 
    file_handler = logging.FileHandler('logs/packet.log')
except: 
    file_handler = logging.FileHandler('src/logs/packet.log')
logger.addHandler(file_handler)

Packet = namedtuple('Packet', ['source', 'destination', 'timestamp', 'destination_port'])

def parse_packet(packet: PKT): 
    try: 
        if 'tcp' in (layer.layer_name for layer in packet.layers): 
            dst_port = packet['tcp'].dstport
        else: 
            dst_port = None
        return Packet(packet['ip'].src, packet['ip'].dst, packet.sniff_timestamp, dst_port)
    except KeyError as e: 
        if 'ipv6' in (layer.layer_name for layer in packet.layers): 
            logger.debug('ipv6 packet detected... skipping') 
            return None 
        else: 
            logger.error(e)
            return None 

def load_traces(path: str = DATA_PATH) -> tuple: 
    pcap_paths, ts_paths = map(glob, map(partial(join, path), ['*.pcap', '*.times'])) 
    if len(pcap_paths) == 0: 
        logger.warn(f'no pcap traces found... ensure a *.pcap file appears in {trace_path}')
    elif len(ts_paths) == 0: 
        logger.warn(f'no timestamp file found... proceeding without timestamp correlation')
    elif len(pcap_paths) > 1: 
        logger.warn(f'Found {len(pcap_paths)} pcap traces... using {pcap_paths[0]}')
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
    logger.info(f"Loaded [{n_loaded}/{n_packets}] succesfully... {errors} loading errors")
    return packet_stream 

