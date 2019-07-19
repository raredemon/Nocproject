# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "BDCOM.xPON.get_chassis_id"
    implements = [IGetChassisID]
    cache = True

    rx_mac = re.compile(r"^Base ethernet MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                macs = []
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.2.2.1.6.289"], bulk=True):
                        macs += [v[1]]
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_mac.search(self.cli("show version", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
