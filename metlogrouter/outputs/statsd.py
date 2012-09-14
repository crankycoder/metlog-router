# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****

import statsd
from types import StringTypes


class StatsdOutput(object):
    """
    Send messages to statsd
    """

    def __init__(self, name, hosts):
        self.name = name

        if isinstance(hosts, StringTypes):
            hosts = [hosts]

        self.hosts = []

        for h in hosts:
            if ':' in h:
                h, port = h.split(':')
                port = int(port)
            else:
                port = 8125

            self.hosts.append((h, port))

        self.clients = []
        for h, port in self.hosts:
            self.clients.append(statsd.StatsClient(h, port))

    def counter(self, msg):

        for client in self.clients:
            # TODO: how are we supposed to use the ns key here?
            client.incr(key, value, rate)

    def timer(self, msg):
        ns = msg['fields']['logger']
        key = msg['fields']['name']
        value = float(msg['payload'])
        rate = float(msg['fields']['rate'])

        for client in self.clients:
            # TODO: how are we supposed to use the ns key here?
            client.timing(key, value, rate)

    def deliver(self, msg):
        ns = msg['fields']['logger']
        key = msg['fields']['name']
        value = float(msg['payload'])
        rate = float(msg['fields']['rate'])

        if fields['type'] == 'counter':
            self.counter(msg)
        elif fields['type'] == 'timer':
            self.timer(msg)
