#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client can run at any one time on one TCP/IP host.

Requires ClientAuth document.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_mqtt_client.py -p -e
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_mqtt_client import CmdMQTTClient

from scs_host.client.mqtt_client import MQTTClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTClient()
    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        auth = ClientAuth.load_from_host(Host)

        if auth is None:
            print("ClientAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(auth, file=sys.stderr)


        client = MQTTClient()
        client.connect(ClientAuth.MQTT_HOST, auth.client_id, auth.user_id, auth.client_password)

        if cmd.verbose:
            print(client, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.publish:
            for line in sys.stdin:
                datum = json.loads(line, object_pairs_hook=OrderedDict)

                while True:
                    publication = Publication.construct_from_jdict(datum)

                    try:
                        if cmd.verbose:
                            now = LocalizedDatetime.now()
                            print("%s:         mqtt: %s" % (now.as_iso8601(), datum['payload']['rec']), file=sys.stderr)
                            sys.stderr.flush()

                        payload = JSONify.dumps(publication.payload)

                        success = client.publish(publication.topic, payload, ClientAuth.MQTT_TIMEOUT)

                        if cmd.verbose and not success:
                            now = LocalizedDatetime.now()
                            print("%s:         mqtt: abandoned" % now.as_iso8601(), file=sys.stderr)
                            sys.stderr.flush()

                        break

                    except Exception as ex:
                        if cmd.verbose:
                            print("%s" % JSONify.dumps(ExceptionReport.construct(ex)))
                            sys.stderr.flush()

                    time.sleep(random.uniform(1.0, 2.0))           # Don't hammer the client!

                if cmd.verbose:
                    now = LocalizedDatetime.now()
                    print("%s:         mqtt: done" % now.as_iso8601(), file=sys.stderr)
                    print("-", file=sys.stderr)
                    sys.stderr.flush()

                if cmd.echo:
                    print(line, end="")
                    sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("mqtt_client: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()