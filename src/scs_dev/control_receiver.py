#!/usr/bin/env python3

"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The function of the control_receiver utility is execute commands received over a messaging topic. In addition to
enabling secure remote management, the utility provides a secure challenge-response facility.

A typical South Coast Science device is provided with a messaging topic whose purpose is to enable bidirectional
command-and-response communications between the device and one or more remote management systems. Commands
are in the form of a specific JSON format, which is validated as follows:

* the message must identify the device as the recipient
* the digest in the incoming message matches the digest computed by the device
* the command must be listed in the device's ~/SCS/cmd/ directory, or be "?"

The digest is computed using a shared secret generated by the scs_mfr/shared_secret utility.

If validated, the control_receiver utility executes the command, then publishes a receipt message which includes:

* the command stdout
* the command stderr
* the command return code
* the original message digest
* a new message digest

Entries in ~/SCS/cmd/ are typically symbolic links to commands that are implemented elsewhere, either by the operating
system, or by South Coast Science packages.

It is the responsibility of the device administrator to mange the ~/SCS/cmd/ directory. Care should be taken to exclude
commands that:

* could cause harm to the system
* require an interactive mode
* require root privileges
* can change the contents of the ~/SCS/cmd/ directory

SYNOPSIS
control_receiver.py [-r] [-e] [-v]

EXAMPLES
( cat ~/SCS/pipes/control_subscription_pipe & ) | ./osio_topic_subscriber.py -cX | ./control_receiver.py -r -v

FILES
~/SCS/cmd/*
~/SCS/conf/system_id.json
~/SCS/conf/shared_secret.json

DOCUMENT EXAMPLE - REQUEST
{"/orgs/south-coast-science-dev/development/device/alpha-pi-eng-000006/control":
{"tag": "bruno", "attn": "scs-ap1-6", "rec": "2018-04-04T14:41:11.872+01:00", "cmd_tokens": ["?"],
"digest": "bf682976cb45d889dfbb7ebdecd207bf3e3b4a6e12336859a93d7023b8454514"}}

DOCUMENT EXAMPLE - RESPONSE
{"/orgs/south-coast-science-dev/development/device/alpha-pi-eng-000006/control":
{"tag": "scs-ap1-6", "rec": "2018-04-04T13:41:59.521+00:00",
"cmd": {"cmd": "?", "params": [],
"stdout": ["[\"afe_baseline\", \"afe_calib\", \"opc_power\", \"ps\", \"schedule\", \"shared_secret\"]"],
"stderr": [], "ret": 0},
"omd": "40ef7a9c0f70033bbe21827ed25286b448a5ad3ace9b16f44f3d94da6a89ab25",
"digest": "597f8de3852f1067f52f126398777abdba6c204c378e8f5d30bad6d8d99ee536"}}

SEE ALSO
scs_analysis/aws_mqtt_control
scs_analysis/osio_mqtt_control
scs_mfr/shared_secret
"""

import json
import sys

from collections import OrderedDict

from scs_core.control.command import Command
from scs_core.control.control_datum import ControlDatum
from scs_core.control.control_receipt import ControlReceipt

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.shared_secret import SharedSecret
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_control_receiver import CmdControlReceiver

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # config...

    deferred_commands = ('reboot', 'restart')


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdControlReceiver()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ------------------------------------------------------------------------------------------------------------
    # resources...

    # SystemID...
    system_id = SystemID.load(Host)

    if system_id is None:
        print("control_receiver: SystemID not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print(system_id, file=sys.stderr)

    # SharedSecret...
    secret = SharedSecret.load(Host)

    if secret is None:
        print("control_receiver: SharedSecret not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print(secret, file=sys.stderr)
        sys.stderr.flush()

    system_tag = system_id.message_tag()
    key = secret.key


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            # control...
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            try:
                datum = ControlDatum.construct_from_jdict(jdict)
            except TypeError:
                continue

            if datum.attn != system_tag:
                continue

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            if not datum.is_valid(key):
                print("control_receiver: invalid digest: %s" % datum, file=sys.stderr)
                sys.stderr.flush()
                continue

            if cmd.echo:
                print(JSONify.dumps(datum))
                sys.stdout.flush()

            # command...
            command = Command.construct_from_tokens(datum.cmd_tokens)

            if command.cmd is not None and not command.is_valid(Host):
                command.error("invalid command")

            # execute immediate commands...
            elif command.cmd not in deferred_commands:
                command.execute(Host)

            # receipt...
            if cmd.receipt:
                now = LocalizedDatetime.now()
                receipt = ControlReceipt.construct_from_datum(datum, now, command, key)

                print(JSONify.dumps(receipt))
                sys.stdout.flush()

                if cmd.verbose:
                    print(JSONify.dumps(receipt), file=sys.stderr)
                    sys.stderr.flush()

            # execute deferred commands...
            if command.cmd in deferred_commands:
                command.execute(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("control_receiver: KeyboardInterrupt", file=sys.stderr)
