"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampler(object):
    """unix command line handler"""

    def __init__(self, default_interval=1):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-i INTERVAL] [-n SAMPLES] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--interval", "-i", type="float", nargs=1, action="store", dest="interval",
                                 default=default_interval,
                                 help="sampling interval in seconds (default %0.1f)" % default_interval)

        self.__parser.add_option("--samples", "-n", type="int", nargs=1, action="store", default=0, dest="samples",
                                 help="number of samples (default for-ever = 0)")

        self.__parser.add_option("--log", "-l", type="string", nargs=1, dest="log", default=False,
                                 help="append exceptions to log")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def interval(self):
        return self.__opts.interval


    @property
    def samples(self):
        return self.__opts.samples


    @property
    def log(self):
        return self.__opts.log


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdSampler:{interval:%0.1f, samples:%d, log:%s, verbose:%s, args:%s}" % \
                    (self.interval, self.samples, self.log, self.verbose, self.args)
