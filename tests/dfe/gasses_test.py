#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.json import JSONify

from scs_core.gas.afe_baseline import AFEBaseline
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.pt1000_calib import Pt1000Calib

from scs_core.sys.system_id import SystemID

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.pt1000 import Pt1000
from scs_dfe.gas.pt1000_conf import Pt1000Conf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_ndir.gas.ndir import NDIR


# --------------------------------------------------------------------------------------------------------------------

# SystemID...
system_id = SystemID.load_from_host(Host)

if system_id is None:
    print("SystemID not available.", file=sys.stderr)
    exit()

# NDIR...
ndir = NDIR.find(Host.ndir_device())

# SHT...
sht_conf = SHTConf.load_from_host(Host)
sht = sht_conf.int_sht()

# Pt1000...
pt1000_conf = Pt1000Conf.load_from_host(Host)
pt1000_calib = Pt1000Calib.load_from_host(Host)
pt1000 = Pt1000(pt1000_calib)

# AFE...
afe_baseline = AFEBaseline.load_from_host(Host)

calib = AFECalib.load_from_host(Host)
sensors = calib.sensors(afe_baseline)


try:
    I2C.open(Host.I2C_SENSORS)

    sampler = GasesSampler(system_id, ndir, sht, pt1000_calib, pt1000, sensors, 1)
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
