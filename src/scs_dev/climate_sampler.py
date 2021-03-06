#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The climate_sampler utility reads a Sensirion SHT 31 (or equivalent) sensor - it therefore provides a measurement of
temperature and relative humidity. Output values are in degrees centigrade and percentage, respectively.

The climate_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document with
fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

South Coast Science equipment may carry one or two SHT sensors. The configuration is specified by the
scs_mfr/sht_conf utility.

SYNOPSIS
climate_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./climate_sampler.py -i10

FILES
~/SCS/conf/schedule.json
~/SCS/conf/sht_conf.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T13:09:49.648+00:00", "val": {"hmd": 66.2, "tmp": 21.7}}

SEE ALSO
scs_dev/scheduler
scs_mfr/schedule
scs_mfr/sht_conf
scs_mfr/system_id

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.climate_sampler import ClimateSampler

from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("climate_sampler: %s" % cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
            print("climate_sampler: %s" % system_id, file=sys.stderr)

        # SHTConf...
        sht_conf = SHTConf.load(Host)

        if sht_conf is None:
            print("climate_sampler: SHTConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("climate_sampler: %s" % sht_conf, file=sys.stderr)

        # SHT...
        sht = sht_conf.ext_sht()

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        sampler = ClimateSampler(runner, tag, sht)

        if cmd.verbose:
            print("climate_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:      climate: %s" % (now.as_time(), sample.rec.as_time()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("climate_sampler: KeyboardInterrupt", file=sys.stderr)

    finally:
        I2C.close()
