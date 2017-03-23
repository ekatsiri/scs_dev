"""
Created on 19 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdTopicPublisher(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -t TOPIC | -c { C | G | P | S } } [-e] [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--channel", "-c", type="string", nargs=1, action="store", dest="channel",
                                 help="publication channel")

        # optional...
        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.topic) == bool(self.channel):
            return False

        if self.channel:
            if self.channel != 'C' and self.channel != 'G' and self.channel != 'P' and self.channel != 'S':
                return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic(self):
        return self.__opts.topic


    @property
    def channel(self):
        return self.__opts.channel


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdTopicPublisher:{topic:%s, channel:%s, echo:%s, verbose:%s, args:%s}" % \
                    (self.topic, self.channel, self.echo, self.verbose, self.args)
