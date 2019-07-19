# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

__author__ = 'Raredemon'

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "BDCOM.xPON.get_config"
    implements = [IGetConfig]

    def execute(self):
        # Fallback to CLI
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 4)
        return self.cleaned_config(config)
