#!/usr/bin/python

def run_net(net):
    """
    Starts the Mininet network, sets static ARP entries, disables rx/tx offloading on hosts,
    and disables IPv6 on all hosts and switches.
    """
    net.start()
    net.staticArp()

    # disabling offload for rx and tx on each host interface
    for host in net.hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        # disable ipv6
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")


