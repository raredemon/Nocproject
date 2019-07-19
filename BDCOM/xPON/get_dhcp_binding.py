# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import datetime
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetDHCPBinding


class Script(noc.sa.script.Script):
    name = "BDCOM.xPON.get_dhcp_binding"
    implements = [IGetDHCPBinding]

    rx_line = re.compile(
        r"^(?P<mac>\S+\:\S+\:\S+\:\S+:\S+:\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<expire>\S+?)\s+(?P<type>DHCP_SN|Manual)\s+(?P<vlan>\d+)\s+(?P<interface>\S+)",
        re.IGNORECASE)

    def execute(self):
        data = self.cli("sh ip dhcp-relay snooping binding all")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip().lower())
            if match:
                delta = match.group("expire")
                r.append({
                    "mac": match.group("mac"),
                    "ip": match.group("ip"),
                    "expiration": datetime.datetime.now() + datetime.timedelta(seconds=int(delta)),
                    "type": match.group("type")[0:4].upper(),
                    "vlan": match.group("vlan"),
                    "interface": match.group("interface"),
                })
        return r
