# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, InterfaceTypeError


class Script(NOCScript):
    name = "BDCOM.xPON.get_interfaces"
    implements = [IGetInterfaces]

    rx_port = re.compile(
        r"(?P<port>(g\d/\d)|(epon\d/\d:\d)|(epon\d/\d)|(v\d+)|(p\d))\s+",
    re.MULTILINE)

    rx_sh_int = re.compile(
        r"^(?P<interface>(\S+\d/\d:\d)|(\S+\d/\d)|(\S+\d{1,4}))\s+is\s+(?P<admin_status>administratively\s+down|up|down),\s+line\s+protocol\s+is\s+(?P<line_status>up|down)\s+Ifindex\s+is\s+(?P<snmp_ifindex>\d{1,3})(?:,\s+unique\s+port\s+number\s+is\s+\d{1,3})?\s+Description:\s+(?P<desc>(\".*\")|(\S+))"
        r"\s+Hardware\s+is\s+(?P<hardware>\S+),\s+[Aa]ddress\s+is\s+(?P<mac>\w{4}.\w{4}.\w{4})",
    re.MULTILINE | re.IGNORECASE )
    
    rx_ip = re.compile(
        r"(?P<interface>\S+)\s+is\s+(up|down),\s+line\s+protocol\s+is\s+(up|down)\s+Internet\s+address\s+is\s+(?P<ip_address>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,2})",
    re.MULTILINE | re.IGNORECASE)

    def get_ports(self, interface=None):
        cmd = self.cli("show interface brief")
        ports = []
        for match in self.rx_port.finditer(cmd):
            port = match.group("port")
            ports += [{
                "port": port.replace('g', 'Gi'),
            }]
        return ports

    def execute(self):
        get_ports = self.get_ports()
        interfaces = []

        # Get switchports and vlans
        switchports = {} 
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"],
            )
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # Get LLDP interfaces
        lldp = []
        for lldp_int in self.scripts.get_lldp_neighbors():
            lldp += [lldp_int['local_interface']]

        # Get IPv4 interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        c_iface = None
        cmd = self.cli("show ip interface", cached=True)
        for match in self.rx_ip.finditer(cmd):
            c_iface = self.profile.convert_interface_name(match.group("interface"))
            ip = match.group("ip_address")
            ipv4_interfaces[c_iface] += [ip]
        
        # Get full list of interface
        for intf in get_ports:
            cmd = self.cli("show interface " + intf['port'], cached=True)
            for match in self.rx_sh_int.finditer(cmd):
                full_ifname = match.group("interface")
                ifname = self.profile.convert_interface_name(full_ifname)
                a_stat = match.group("admin_status").lower() == "up"
                o_stat = match.group("line_status").lower() == "up"
                hw = match.group("hardware")
                mac = match.group("mac")
                snmp_ifindex = match.group("snmp_ifindex")
                desc = match.group("desc")
                desc = desc.replace('"', '')
                encaps = 'ARPA'
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "enabled_afi": [],
                    "enabled_protocols": []
                }
            if desc:
                sub["description"] = desc
            if mac:
                sub["mac"] = mac
            if ifname in switchports and ifname not in portchannel_members:
                
                sub["enabled_afi"] += ["BRIDGE"]
                untagged, tagged = switchports[ifname]
                if untagged:
                    sub["untagged_vlan"] = untagged
                if tagged:
                    sub["tagged_vlans"] = tagged
            # Static vlans
            if encaps:
                #encaps = match.group("encaps")
                if encaps[:6] == "802.1Q":
                    sub["vlan_ids"] = [encaps.split(",")[1].split()[2][:-1]]
            # IPv4/Ipv6
            if ip:
                if ifname in ipv4_interfaces:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = ipv4_interfaces[ifname]
            # Setting interface type
            if hw == 'PortAggregator':
                iftype = 'aggregated'
            elif hw == 'EtherSVI':
                iftype = 'SVI'
            else:
                iftype = 'physical'

            iface = {
                "name": ifname,
                "snmp_ifindex": snmp_ifindex,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "type": iftype,
                "enabled_protocols": [],
                "subinterfaces": [sub]
            }
            if ifname in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            if desc:
                iface["description"] = desc
            if "mac" in sub:
                iface["mac"] = sub["mac"]
            # Set VLAN IDs for SVI
            if iface["type"] == "SVI":
                sub["vlan_ids"] = [full_ifname[4:]]
            
            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                iface["enabled_protocols"] += ["LACP"]
            interfaces += [iface]

        return [{"interfaces": interfaces}]
