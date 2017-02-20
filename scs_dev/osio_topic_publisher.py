#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Mey require Publication document.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_topic_publisher.py -e -t /users/southcoastscience-dev/test/json
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.client.topic_client import TopicClient
from scs_core.osio.config.publication import Publication
from scs_core.sys.device_id import DeviceID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_topic_publisher import CmdTopicPublisher

from scs_host.client.mqtt_client import MQTTClient
from scs_host.sys.host import Host


# TODO: make this work with HTTP PUT

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicPublisher()
    if cmd.verbose:
        print(cmd, file=sys.stderr)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        auth = ClientAuth.load_from_host(Host)

        if auth is None:
            print("ClientAuth not available.")
            exit()

        if cmd.verbose:
            print(auth, file=sys.stderr)

        device_id = DeviceID.load_from_host(Host)

        if device_id is None:
            print("DeviceID not available.")
            exit()

        if cmd.verbose:
            print(device_id, file=sys.stderr)


        if cmd.channel:
            publication = Publication.load_from_host(Host)

            if publication is None:
                print("Publication not available.")
                exit()

            if cmd.channel == 'C':
                topic = publication.climate_topic()

            elif cmd.channel == 'G':
                topic = publication.gases_topic()

            elif cmd.channel == 'P':
                topic = publication.particulates_topic()

            else:
                topic = publication.status_topic(device_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print(topic, file=sys.stderr)


        client = MQTTClient()
        publisher = TopicClient(client, auth)

        if cmd.verbose:
            print(publisher, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = json.loads(line, object_pairs_hook=OrderedDict)

            while True:
                try:
                    publisher.publish(topic, datum)
                    break
                except:
                    pass

            if cmd.echo:
                print(line, end="")
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_topic_publisher: KeyboardInterrupt", file=sys.stderr)

    # except Exception as ex:
    #     print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
