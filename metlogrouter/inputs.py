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
#   Rob Miller (rmiller@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from gevent import select, socket
import gevent


class UdpInput(object):
    """
    Simple UDP socket listener.
    """
    def __init__(self, host='', port=0):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.active_host, self.active_port = self.socket.getsockname()

    def __unicode__(self):
        return "Running UDP listener on %s:%s" % (self.active_host,
                self.active_port)

    def start(self, queue):
        while True:
            result = select.select([self.socket], [], [])
            data, addr = result[0][0].recvfrom(60000)
            queue.put(data)
            gevent.sleep(0)
