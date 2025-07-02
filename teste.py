from load_topology import *
from aux import *

if __name__ == '__main__':
    NETWORKX_TOPO = loadNXtopology()
    print("\nStarting mininet...")
    MN_NET = loadMininet(NETWORKX_TOPO)
    MN_NET.start()

    hosts = MN_NET.hosts
    print(f'hosts: {hosts}')