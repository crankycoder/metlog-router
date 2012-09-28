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
#   Rob Miller (rmiller@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from gevent.queue import Empty, Queue
from metlogrouter.decoders.json import JSONDecoder
from nose import SkipTest
from nose.tools import eq_
import gevent

import json


try:
    from metlogrouter.decoders.msgpack import MsgPackDecoder
    import msgpack
except ImportError:
    MsgPackDecoder = None  # NOQA


class TestJsonDecoder(object):
    def setup(self):
        self.out_q = Queue()

    def test_json(self):
        MSG = {'foo': 'bar'}
        greenlets = []
        decoder = JSONDecoder()

        def insert_json_obj():
            decoder.queue.put(json.dumps(MSG))

        def check_queue(output_queue):
            while True:
                try:
                    eq_(MSG, output_queue.get(block=False))
                    gevent.killall(greenlets)
                except Empty:
                    pass
                gevent.sleep(0)

        greenlets.append(gevent.spawn(decoder.start, self.out_q))
        greenlets.append(gevent.spawn(insert_json_obj))
        greenlets.append(gevent.spawn(check_queue, self.out_q))
        gevent.joinall(greenlets)


class TestMsgPackDecoder(object):
    def setup(self):
        if MsgPackDecoder is None:
            raise SkipTest
        self.out_q = Queue()

    def test_msgpack(self):
        MSG = {'foo': 'bar'}
        greenlets = []
        decoder = MsgPackDecoder()

        def insert_msgpack_obj():
            decoder.queue.put(msgpack.dumps(MSG))

        def check_queue(output_queue):
            while True:
                try:
                    eq_(MSG, output_queue.get(block=False))
                    gevent.killall(greenlets)
                except Empty:
                    pass
                gevent.sleep(0)

        greenlets.append(gevent.spawn(decoder.start, self.out_q))
        greenlets.append(gevent.spawn(insert_msgpack_obj))
        greenlets.append(gevent.spawn(check_queue, self.out_q))
        gevent.joinall(greenlets)
