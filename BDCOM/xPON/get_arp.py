# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "BDCOM.xPON.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(
        r"^\s+IP\s+(?P<ip>(\d{1,4}.\d{1,4}.\d{1,4}.\d{1,4}))\s+(?P<age>\d+)\s+(?P<mac>\S+)\s+ARPA+\s+\S+\((?P<interface>\S+)\)$", 
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            intf = match.group("interface")
            intf = intf.replace('g', 'gi')
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": intf
            }]
        return r
