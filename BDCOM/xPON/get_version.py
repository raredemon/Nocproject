# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.3310C.get_version
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "BDCOM.xPON.get_version"
    implements = [IGetVersion]
    cache = True

    rx_version = re.compile(
        r"BDCOM\(tm\)\s+(?P<platform>\S+)\s+Software,\s+Version\s+(?P<version>\S+)\s+Build\s+(?P<build>\d+)", re.MULTILINE)
    rx_hardware = re.compile(
        r"hardware\s+version:(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial = re.compile(
        r"Serial\s+num:(?P<serial>\d+)$", re.MULTILINE)
        #r"ROM:\s+System\s+Bootstrap,\s+Version\s+(?P<version>\S+),\s+Serial\s+num:(?P<serial>\d+)$", re.MULTILINE)


    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                data = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                data = data.decode("utf-8")
                data = str(data).rstrip("u")
                match = self.re_search(self.rx_version, data)
                platform, version, build = match.group("platform", "version", "build")
                match = self.re_search(self.rx_serial, data)
                serial = match.group("serial")
                return {
                        "vendor": "BDCOM",
                        "platform": platform,
                        "version": version,
                        "build": build,
                        "attributes": {
                            "HW version": 'V1.0',
                            "Serial Number": serial,
                            }
                        }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        ver = self.cli("show version", cached=True)
        platform = self.re_search(self.rx_version, ver)
        version = self.re_search(self.rx_version, ver)
        build = self.re_search(self.rx_version, ver)
        serial = self.re_search(self.rx_serial, ver)
        hardware = self.re_search(self.rx_hardware, ver)

        return {
                "vendor": "BDCOM",
                "platform": platform.group("platform"),
                "version": version.group("version"),
                "build": version.group("build"),
                "attributes": {
                    "HW version": hardware.group("hardware"),
                    "Serial Number": serial.group("serial"),
                    }
                }