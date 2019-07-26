# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.dom_status
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDOMStatus
import re


class Script(NOCScript):
    name = "BDCOM.xPON.get_dom_status"
    implements = [IGetDOMStatus]
    rx_line = re.compile(r"(?P<interface>epon(\d/\d))\s+(?P<temp_c>(\d+.\d))\s+(?P<voltage_v>((\d+.\d)))\s+(?P<current_ma>((\d+.\d)))\s+(?P<optical_tx_dbm>((\d+.\d)))\s+(?P<optical_rx_dbm>)", 
        re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        s = self.cli("sh epon optical-transceiver-diagnosis")
        r = []
        for line in s.splitlines():
            for match in self.rx_line.finditer(line):
                interface = match.group("interface")
                temp_c = match.group("temp_c")
                if temp_c == "N/A" or temp_c == "N/S":
                    temp_c = None
                voltage_v = match.group("voltage_v")
                if voltage_v == "N/A" or voltage_v == "N/S":
                    voltage_v = None
                current_ma = match.group("current_ma")
                if current_ma == "N/A" or current_ma == "N/S":
                    current_ma = None
                optical_tx_dbm = match.group("optical_tx_dbm")
                if optical_tx_dbm == "N/A" or optical_tx_dbm == "N/S":
                    optical_tx_dbm = None
                # Optical rx is always == None
                #optical_rx_dbm = match.group("optical_rx_dbm")
                #if optical_rx_dbm == "N/A" or optical_rx_dbm == "N/S":
                optical_rx_dbm = None
                r.append({
                    "interface": interface,
                    "temp_c": temp_c,
                    "voltage_v": voltage_v,
                    "current_ma": current_ma,
                    "optical_rx_dbm": optical_rx_dbm,
                    "optical_tx_dbm": optical_tx_dbm
                })
        return r
