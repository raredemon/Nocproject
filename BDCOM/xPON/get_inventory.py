# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError

class Script(NOCScript):
    name = "BDCOM.xPON.get_inventory"
    implements = [IGetInventory]

    rx_version = re.compile(
        r"^(?P<vendor>\S+)\(tm\)\s+(?P<part_no>\S+)\s+Software,\s+Version\s+(?P<version>\S+)\s+Build\s+(?P<build>\d+)", re.MULTILINE)

    rx_serial = re.compile(
        r"Serial\s+num:(?P<serial>\d+)$", re.MULTILINE)

    rx_hardware = re.compile(
        r"hardware\s+version:(?P<revision>\S+)$", re.MULTILINE)

    def execute(self):
        ver = self.cli("show version", cached=True)
        version = self.re_search(self.rx_version, ver)
        serial = self.re_search(self.rx_serial, ver)
        hardware = self.re_search(self.rx_hardware, ver)

        r = [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": version.group("vendor"),
            "part_no": [version.group("part_no")],
            "revision": hardware.group("revision"),
            "serial": serial.group("serial"),
            "description": version.group("part_no")
        }]
        return r
