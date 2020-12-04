import os 
from pathlib import Path 

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
PCAP_PATH = 'https://data.caida.org/datasets/passive-2018/equinix-nyc/20180419-130000.UTC/equinix-nyc.dirA.20180419-133149.UTC.anon.pcap.gz'
PCAP_TIMES_PATH = 'https://data.caida.org/datasets/passive-2018/equinix-nyc/20180419-130000.UTC/equinix-nyc.dirA.20180419-133149.UTC.anon.times.gz'
PCAP_STATS_PATH = 'https://data.caida.org/datasets/passive-2018/equinix-nyc/20180419-130000.UTC/equinix-nyc.dirA.20180419-133149.UTC.anon.pcap.stats'


BIT = 1 
BYTE = 8 * BIT 
WORD_SIZE = 4 * BYTE 

