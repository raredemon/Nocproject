# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_subscriber_sessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
import re

class Script(noc.sa.script.Script):
    name = "Cisco.IOS.get_subscriber_sessions"
    #implements = [IGetARP]
    rx_session = re.compile(
        r"Type:\s+(?P<sess_type>(DHCPv4|PPPoE|IPv4)),\s+UID:\s+(?P<uid>\d+),\s+State:\s+(?P<state>(authen|unauthen)),\s+Identity:\s+(?P<identity>\S+)\nIPv4\s+Address:\s+(?P<ip>\d+\.\d+\.\d+\.\d+)(?:\s+)\nSession\s+Up-time:\s+(?P<uptime>(\S+\s+|\S+)),"
        , re.MULTILINE | re.DOTALL | re.VERBOSE)

    def execute(self):
        cmd = self.cli("show subscriber session detailed", cached = True)
        r = []
        for match in self.rx_session.finditer(cmd):
            r.append({
                "type": match.group("sess_type"),
                "uid": match.group("uid"),
                "state": match.group("state"),
                "login": match.group("identity"),
                "ip": match.group("ip"),
                "uptime": str(match.group("uptime")).strip(),
                "bras": str(self.object_name).encode("utf-8"),
            })
            

        return r
