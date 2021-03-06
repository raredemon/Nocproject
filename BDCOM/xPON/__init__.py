# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: BDCOM
## OS:     Version 10.1.0E Build 58597
##----------------------------------------------------------------------
## Copyright (C) 2019-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(NOCProfile):
    name = "BDCOM.xPON"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^Username:"
    pattern_password = r"^Password:"
    pattern_more = [
        (r"^More: <space>,  Quit: q, One line: <return>$", " "),
        (r"^\s+--More--\s+", " "),
        ]
    pattern_unpriveleged_prompt = r"^[\S+\s+]+\>$"
    pattern_syntax_error = r"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered|bad parameter value)$"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "write all"
    pattern_prompt = r"\S+#"
    default_parser = "noc.cm.parsers.BDCOM.xPON.base.BasexPONParser"
    # def convert_interface_name(self, interface):
    #     return self.convert_interface_name_cisco(interface)

    def convert_interface_name(self, interface):
        il = interface.lower()
        if il.startswith("epon"):
            return "Epon" + interface[4:]
        if il == "all":
            return "all"
        return self.convert_interface_name_cisco(interface)
