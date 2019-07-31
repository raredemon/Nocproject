# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "BDCOM.xPON.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_local_int = re.compile(r"(?P<local_int>Gig\d/\d)",re.MULTILINE)
    rx_chassis = re.compile(r"^chassis\s+id:\s+(?P<chassis_id>\S+)",re.MULTILINE)
    rx_port = re.compile(r"^port\s+id:\s+(?P<port_id>\S+)",re.MULTILINE)
    rx_desc = re.compile(r"^port\s+description:\s+(?P<port_desc>\S+)",re.MULTILINE)
    rx_sys_name = re.compile(r"^system\s+name:\s+(?P<sys_name>\S+)",re.MULTILINE)
    rx_sys_cap = re.compile(r"^system\s+capabilities:\s+(?P<sys_cap>\S+\s+\S+)",re.MULTILINE)
    rx_remote_ip = re.compile(r"^Management\s+Address:\s+IP:\s+(?P<remote_ip>\S+)",re.MULTILINE)

    CAPS_MAP = {
        "O": 1, "r": 2, "B": 4,
        "W": 8, "R": 16, "T": 32,
        "C": 64, "S": 128, "D": 256,
        "H": 512, "TP": 1024,
    }

    def execute(self):
        r = []
        cmd = self.cli("show lldp neighbors", cached=True)
        for match in self.rx_local_int.finditer(cmd):
            port = match.group("local_int")
            cmd = self.cli("show lldp neighbors interface " + port, cached=True)
            chassis_id = self.re_search(self.rx_chassis, cmd)
            port_id = self.re_search(self.rx_port, cmd)
            port_desc = self.re_search(self.rx_desc, cmd)
            sys_name = self.re_search(self.rx_sys_name, cmd)
            sys_cap = self.re_search(self.rx_sys_cap, cmd)
            remote_ip = self.re_search(self.rx_remote_ip, cmd)
            capabilities = sys_cap.group("sys_cap")
            cap = 0
            for c in capabilities.split(" "):
                c = c.strip()
                if c:
                    cap |= self.CAPS_MAP[c]
            r += [{
                "neighbors": [
                    {
                        "remote_port_subtype": 128,
                        "remote_port": port_id.group("port_id"),
                        "remote_port_description": port_desc.group("port_desc"),
                        "remote_capabilities": cap,
                        "remote_chassis_id": chassis_id.group("chassis_id"),
                        "remote_system_name": sys_name.group("sys_name"),
                        "remote_management_address": remote_ip.group("remote_ip"),
                        "remote_chassis_id_subtype": 4
                    }
                ],
                "local_interface": port
            }]

        return r
