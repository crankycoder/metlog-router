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


from nose.tools import eq_
from metlogrouter.inputs import UdpInput
from gevent.queue import Empty, Queue
import gevent


def test_udp_input():
    """
    This test will hang if UDPInput is not working properly
    """
    HOST = ''
    MSG = 'fooobar'

    input = UdpInput(HOST)
    server_port = input.active_port

    q = Queue()
    greenlets = []

    def udp_sender():
        """
        a simple stupid UDP sender
        """
        from gevent import socket
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            sender.sendto(MSG, (HOST, server_port))
            gevent.sleep(0)

    def check_queue(input_queue):
        while True:
            try:
                eq_(MSG, input_queue.get(block=False))
                gevent.killall(greenlets)
            except Empty:
                pass
            gevent.sleep(0)

    greenlets.append(gevent.spawn(input.start, q))
    greenlets.append(gevent.spawn(udp_sender))
    greenlets.append(gevent.spawn(check_queue, q))
    gevent.joinall(greenlets)
