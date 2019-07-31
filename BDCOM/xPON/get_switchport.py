# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "BDCOM.xPON.get_switchport"
    implements = [IGetSwitchport]

    rx_port = re.compile(
        r"^(?P<port>(g\d/\d)|(epon\d/\d:\d)|(epon\d/\d)|(v\d+)|(p\d))\s+(?P<desc>(\".*\")|(\S+))\s+(?P<state>up|down)",
        re.MULTILINE
    )
    rx_vlan = re.compile(
        r"^(?P<port>(GigaEthernet\d/\d)|(EPON\d/\d)|(Port-aggregator\d))\s+(?P<property>\S+)\s+(?P<pvid>\d)\s+(?P<vlan>(\d{1,4})(,|-)(\d{1,4}))\s+(?P<vlan_map>\S+)\s+(?P<vlan1>(\d{1,4})(,|-)(\d{1,4}))\s+$",
        re.MULTILINE
    )
    rx_vlan_access = re.compile(
        r"^\s+epon\s+onu\s+port\s+\d\s+ctc\s+vlan\s+mode\s+tag\s+(?P<vlan>\d{1,4})",
        re.MULTILINE  
    )
    rx_member = re.compile(
        r"^((?P<member>g\d/\d)\((\S{2,3})\)\s+){2,6}",
        re.MULTILINE  
    )

    def get_ports(self, interface=None):
        cmd = self.cli("show interface brief")
        ports = []
        for match in self.rx_port.finditer(cmd):
            port = match.group("port")
            desc = match.group("desc")
            state = match.group("state")
            ports += [{
                "port": port.replace('g', 'Gi'),
                "desc": desc.strip('"'),
                "state": state,
            }]
        return ports

    def execute(self):
        vlans = []
        ports_data = self.get_ports()
        for intf in ports_data:
            if intf['port'].startswith('p'):
                portchannels = self.scripts.get_portchannel()
                portchannel_members = []
                for p in portchannels:
                    portchannel_members += p["members"]
                cmd_vlan = self.cli("show vlan interface " + intf['port'])
                for match in self.rx_vlan.finditer(cmd_vlan):
                    port = intf['port']
                    status = 'true' if intf['state'] == 'up' else 'false'
                    vlans1 = self.expand_interface_range(match.group("vlan"))
                    vlans2 = self.expand_interface_range(match.group("vlan1"))
                    propety_mode = match.group("property")
                    vlans_ = vlans1.extend(vlans2)
                    vlans += [{
                        "interface": self.profile.convert_interface_name(port.replace('p', 'Po')),
                        "status": status,
                        "tagged": vlans1,
                        "untagged": [],
                        "description": intf['desc'],
                        "members": portchannel_members,
                        "802.1ad Tunnel": 'false',
                        "802.1Q Enabled": 'true',
                    }]

            elif intf['port'].startswith('v'):
                pass #print('if startswith ', intf['port'])

            elif intf['port'].startswith('epon') and ':' in intf['port']:
                cmd_vlan = self.cli("show running-config interface " + intf['port'] + " | include tag")
                for match in self.rx_vlan_access.finditer(cmd_vlan):
                    status = 'true' if intf['state'] == 'up' else 'false'
                    vlan = match.group("vlan")
                    vlans += [{
                            "interface": self.profile.convert_interface_name(intf['port']),
                            "status": status,
                            "tagged": [],
                            "untagged": vlan,
                            "description": intf['desc'],
                            "members": [],
                            "802.1ad Tunnel": 'false',
                            "802.1Q Enabled": 'true',
                        }]

            else:
                cmd_vlan = self.cli("show vlan interface " + intf['port'])
                for match in self.rx_vlan.finditer(cmd_vlan):
                    status = 'true' if intf['state'] == 'up' else 'false'
                    vlans1 = self.expand_interface_range(match.group("vlan"))
                    vlans2 = self.expand_interface_range(match.group("vlan1"))
                    propety_mode = match.group("property")
                    vlans_ = vlans1.extend(vlans2)
                    vlans += [{
                        "interface": intf['port'],
                        "status": status,
                        "tagged": vlans1,
                        "untagged": [],
                        "description": intf['desc'],
                        "members": [],
                        "802.1ad Tunnel": 'false',
                        "802.1Q Enabled": 'true',
                    }]
            
        return vlans
