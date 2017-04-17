#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

command line example:
./particulates_sampler.py -i 10 | \
./osio_topic_publisher.py -e /users/southcoastscience-dev/test/particulates
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    io = None
    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler(10)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        # SystemID...
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # sampler...
        sampler = ParticulatesSampler(system_id, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)

        sampler.off()       # in case it had been left on after the last run

        sampler.on()
        sampler.reset_timer()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s: particulates: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("particulates_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sampler:
            sampler.off()

        I2C.close()
