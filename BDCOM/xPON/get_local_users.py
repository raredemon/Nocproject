# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers
import re
import datetime


class Script(noc.sa.script.Script):
    name = "BDCOM.xPON.get_local_users"
    implements = [IGetLocalUsers]
    rx_line = re.compile(r"^username\s+(?P<username>\S+)(?:\s+.*privilege\s+(?P<privilege>\d+))?.*$")

    def execute(self):
        data = self.cli("show running-config | include username")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                user_class = "operator"
                privilege = match.group("privilege")
                if privilege:
                    if privilege == "15":
                        user_class = "superuser"
                    else:
                        user_class = privilege
                r.append({
                    "username": match.group("username"),
                    "class": user_class,
                    "is_active": True
                    })
        return r
