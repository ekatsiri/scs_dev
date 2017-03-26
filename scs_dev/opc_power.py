#!/usr/bin/env python3

"""
Created on 26 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/opc_power.py -v 0
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.particulate.opc_n2 import OPCN2


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        opc = OPCN2()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            # OPC...
            opc.power_on()
            opc.operations_on()

        else:
            # OPC...
            opc.operations_off()
            opc.power_off()

        if cmd.verbose:
            print(opc, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
