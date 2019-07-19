# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
import noc.sa.script
## NOC modules
from noc.sa.interfaces import IGetFQDN


class Script(noc.sa.script.Script):
    name = "BDCOM.xPON.get_fqdn"
    implements = [IGetFQDN]

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                hostname = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                print('name ibo', hostname)
                return hostname + '.ip.ntl.ru'
            except self.snmp.TimeOutError:
                pass