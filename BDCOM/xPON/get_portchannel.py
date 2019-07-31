# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "BDCOM.xPON.get_portchannel"
    implements = [IGetPortchannel]

    rx_member = re.compile(
        r"(?P<member>g\d/\d)\((\S{2,3})\)",
        re.MULTILINE  
    )

    rx_all = re.compile(
        r"\d+\s+(?P<int>\S{2}\d)(\S+)\s+(?P<member>g\d/\d)\((\S{2,3})\)",
    re.MULTILINE)

    def execute(self):
        cmd = self.cli("show aggregator-group summary", cached = True)
        for match in self.rx_all.finditer(cmd):
            r = [] 
            members = []
            interface = match.group("int")
            for match2 in self.rx_member.finditer(cmd):
                mmbr = match2.group("member")
                mmbr = mmbr.replace('g', 'gi')
                members += [mmbr]
            r += [{
                "interface": interface,
                "type": "L",
                "members": members,
            }]
        return r
