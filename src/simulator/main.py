import argparse

from objects import switches, servers

parser = argparse.ArgumentParser(description='Simulate given packet data over a set of switches.')
parser.add_argument('data_files', metavar='file', type=str, nargs='+',
        help='A file containing sample data to simulate over switches.')
parser.add_argument('-n', dest='n_switches', metavar='num',
        action='store', type=int, default=1,
        help='Number of switches to simulate (default: 1)')
# parser.add_argument('-m', '--servers', dest='n_servers', metavar='num',
#         action='store', type=int, default=1,
#         help='Number of servers to simulate (default: 1)')
parser.add_argument('--switch', choices = switches.keys(),
        default="Standalone Switch")

args = parser.parse_args()
