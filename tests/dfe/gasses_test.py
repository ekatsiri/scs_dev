#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sync.timed_runner import TimedRunner
from scs_core.sys.system_id import SystemID

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.board.dfe_conf import DFEConf
from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_ndir.gas.ndir import NDIR


# --------------------------------------------------------------------------------------------------------------------

try:
    I2C.open(Host.I2C_SENSORS)

    # SystemID...
    system_id = SystemID.load(Host)

    if system_id is None:
        print("SystemID not available.", file=sys.stderr)
        exit(1)

    # NDIR...
    ndir = NDIR(Host.ndir_spi_bus(), Host.ndir_spi_device())       # NDIR.find(Host.ndir_device())

    # SHT...
    sht_conf = SHTConf.load(Host)
    sht = sht_conf.int_sht()

    # AFE...
    dfe_conf = DFEConf.load(Host)
    afe = dfe_conf.afe(Host)

    # runner...
    runner = TimedRunner(0)

    sampler = GasesSampler(runner, system_id, ndir, sht, afe)
    print(sampler)
    print("-")

    sampler.reset()

    datum = sampler.sample()
    print(datum)
    print("-")

    jstr = JSONify.dumps(datum)
    print(jstr)

finally:
    I2C.close()
