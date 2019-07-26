# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.3310C.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "BDCOM.xPON.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(
        r"^(?P<vlanid>\d+)\s+Static\s+(?P<vlanname>VLAN\d+)",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r += [{
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('vlanname')
            }]
        return r
