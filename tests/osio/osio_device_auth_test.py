#!/usr/bin/env python3

"""
Created on 17 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

user_id, system_id, device_password

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}
"""

from scs_core.osio.client.client_auth import ClientAuth

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

user_id = "southcoastscience-dev"
print(user_id)

system_id = "5406"
print(system_id)

device_password = "jtxSrK2e"
print(device_password)

print("-")


# --------------------------------------------------------------------------------------------------------------------

auth = ClientAuth(user_id, system_id, device_password)
print(auth)
print("-")

auth.save(Host)

auth = ClientAuth.load(Host)
print(auth)
print("-")
