"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import subprocess

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.location.gpgga import GPGGA
from scs_core.location.gps_location import GPSLocation
from scs_core.sample.status_datum import StatusDatum
from scs_core.sampler.sampler import Sampler
from scs_core.sys.system_temp import SystemTemp
from scs_core.sys.uptime_datum import UptimeDatum
from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.gps.pam7q import PAM7Q
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class StatusSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, system_id):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__system_id = system_id
        self.__board = MCP9808(True)
        self.__gps = PAM7Q()


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        tag = self.__system_id.message_tag()

        # location...
        location = None

        try:
            self.__gps.open()
            gga = self.__gps.report(GPGGA)
            location = GPSLocation.construct(gga)
        except RuntimeError:
            pass

        finally:
            try:
                self.__gps.close()
            except RuntimeError:
                pass

        # temperature...
        try:
            board_sample = self.__board.sample()
        except OSError:
            board_sample = self.__board.null_datum()

        mcu_sample = Host.mcu_temp()

        temperature = SystemTemp.construct(board_sample, mcu_sample)

        # uptime...
        raw = subprocess.check_output('uptime')
        report = raw.decode()

        uptime = UptimeDatum.construct_from_report(None, report)

        # datum...
        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return StatusDatum(tag, recorded, location, temperature, uptime)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StatusSampler:{runner:%s, system_id:%s, board:%s, gps:%s}" % \
               (self.runner, self.__system_id, self.__board, self.__gps)
