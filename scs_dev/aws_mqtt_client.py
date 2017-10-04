#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client should run at any one time, per a TCP/IP host.

Requires APIAuth and ClientAuth documents.

command line example:
./osio_mqtt_client.py \
/orgs/south-coast-science-dev/unep/loc/1/gases gases.uds \
/orgs/south-coast-science-dev/unep/loc/1/particulates particulates.uds \
-p osio_mqtt_pub.uds -s -e
"""

import json
import logging
import sys
import time

from collections import OrderedDict

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, comms=None, echo=False, verbose=False):
        """
        Constructor
        """
        self.__comms = comms

        self.__echo = echo
        self.__verbose = verbose


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

        # if self.__echo:
        #     print(JSONify.dumps(pub))
        #     sys.stdout.flush()
        #
        # if self.__verbose:
        #     print("received: %s" % JSONify.dumps(pub), file=sys.stderr)
        #     sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTHandler:{comms:%s, echo:%s, verbose:%s}" % \
               (self.__comms, self.__echo, self.__verbose)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    pub_comms = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    host = "asrfh6e5j5ecz.iot.us-west-2.amazonaws.com"
    rootCAPath = "/home/pi/SCS/aws/root-CA.crt"
    certificatePath = "/home/pi/SCS/aws/scs-rpi-006.cert.pem"  # 9f01402232-certificate.pem.crt
    privateKeyPath = "/home/pi/SCS/aws/scs-rpi-006.private.key"  # 9f01402232-private.pem.key
    clientId = "rpi-006"
    topic = "bruno/1"

    # host = "asrfh6e5j5ecz.iot.us-west-2.amazonaws.com"
    # rootCAPath = "/home/pi/SCS/aws/root-CA.crt"
    # certificatePath = "/home/pi/SCS/aws/scs-rpi-006.cert.pem"  # 9f01402232-certificate.pem.crt
    # privateKeyPath = "/home/pi/SCS/aws/scs-rpi-006.private.key"  # 9f01402232-private.pem.key
    # clientId = "rpi-006"
    # topic = "bruno/1"

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.DEBUG)

        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)

        logger.addHandler(streamHandler)

        myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)

        myAWSIoTMQTTClient.configureEndpoint(host, 8883)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(30)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(30)  # 5 sec


        # ------------------------------------------------------------------------------------------------------------
        # run...

        handler = AWSMQTTHandler()

        myAWSIoTMQTTClient.connect()
        myAWSIoTMQTTClient.subscribe(topic, 1, handler.handle)
        time.sleep(2)

        while True:
            time.sleep(2)


            # ----------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        # if cmd.verbose:
        #     print("osio_mqtt_client: KeyboardInterrupt", file=sys.stderr)
        pass

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()
