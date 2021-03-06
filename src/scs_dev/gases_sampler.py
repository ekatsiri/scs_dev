#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The gases_sampler utility reads a set of values from a South Coast Science digital front-end (DFE) board hosting an
Alphasense analogue front-end (AFE) board. The also utility reads an NDIR CO2 sensor, if the appropriate configuration
document is present.

The gases_sampler utility reports raw electrode voltages, temperature-compensated voltages, and gas concentrations
(in parts per billion) derived according to the relevant Alphasense application notes. If the AFE board includes a
Pt1000 temperature sensor, then the gases_sampler utility may also report the Pt1000 voltage and temperature.

The DFE board supports AFEs with up to four electrochemical sensors, or three electrochemical sensors plus one
photo-ionisation detector (PID). Before using the gases_sampler utility, the configuration of the AFE must be
specified using the scs_mfr/afe_calib utility.

Temperature must be known in order to perform a simple data interpretation. The gases_sampler utility applies an
order of precedence for temperature sources, depending on availability:

1. Sensirion SHT in A4 package
2. Free-to-air Sensirion SHT
3. AFE Pt1000 sensor

The presence of the DFE subsystem, and the availability of the Pt1000 sensor on the AFE is specified using the
scs_mfr/dfe_conf utility. The configuration of Sensirion SHT sensor(s) is specified using the scs_mfr/dfe_conf
utility.

Gas concentrations for each sensor are adjusted according to a baseline value, which is specified using the
scs_mfr/afe_baseline utility. This provides a simple way of managing zero-offset drift for each sensor
expressed in parts per billion.

The gases_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document with
fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
gases_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./gases_sampler.py -i10

FILES
~/SCS/conf/afe_baseline.json
~/SCS/conf/afe_calib.json
~/SCS/conf/dfe_conf.json
~/SCS/conf/ndir_conf.json
~/SCS/conf/pt1000_calib.json
~/SCS/conf/sht_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2018-04-05T09:16:12.751+00:00",
"val": {"CO": {"weV": 0.34863, "aeV": 0.268817, "weC": 0.064464, "cnc": 237.0},
"SO2": {"weV": 0.277004, "aeV": 0.276129, "weC": -0.000801, "cnc": 2.2},
"H2S": {"weV": 0.258504, "aeV": 0.222316, "weC": -0.091086, "cnc": 7.2},
"VOC": {"weV": 0.102127, "weC": 0.101793, "cnc": 1294.8},
"sht": {"hmd": 54.4, "tmp": 21.6}}}

SEE ALSO
scs_dev/scheduler
scs_mfr/afe_baseline
scs_mfr/afe_calib
scs_mfr/dfe_conf
scs_mfr/ndir_conf
scs_mfr/pt1000_calib
scs_mfr/schedule
scs_mfr/sht_conf
scs_mfr/system_id

RESOURCES
Alphasense Application Note AAN 803-02
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.board.dfe_conf import DFEConf
from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_ndir.gas.ndir_conf import NDIRConf
except ImportError:
    from scs_core.gas.ndir_conf import NDIRConf


# TODO: test gases service restart - semaphore problem?

# TODO: needs flag to keep NDIR switched on?

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("gases_sampler: %s" % cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
            print("gases_sampler: %s" % system_id, file=sys.stderr)

        # NDIR...
        ndir_conf = NDIRConf.load(Host)
        ndir_monitor = None if ndir_conf is None else ndir_conf.ndir_monitor(Host)

        if cmd.verbose and ndir_conf:
            print("gases_sampler: %s" % ndir_conf, file=sys.stderr)

        # SHT...
        sht_conf = SHTConf.load(Host)
        sht = None if sht_conf is None else sht_conf.int_sht()

        if cmd.verbose and sht_conf:
            print("gases_sampler: %s" % sht_conf, file=sys.stderr)

        # AFE...
        dfe_conf = DFEConf.load(Host)
        afe = None if dfe_conf is None else dfe_conf.afe(Host)

        if cmd.verbose and dfe_conf:
            print("gases_sampler: %s" % dfe_conf, file=sys.stderr)

        if cmd.verbose and afe:
            print("gases_sampler: %s" % afe, file=sys.stderr)

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        sampler = GasesSampler(runner, tag, ndir_monitor, sht, afe)

        if cmd.verbose:
            print("gases_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.verbose and ndir_conf:
            print("gases_sampler: %s" % ndir_monitor.firmware(), file=sys.stderr)
            sys.stderr.flush()

        sampler.start()

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:        gases: %s" % (now.as_time(), sample.rec.as_time()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("gases_sampler: KeyboardInterrupt", file=sys.stderr)

    finally:
        if sampler:
            sampler.stop()

        I2C.close()
