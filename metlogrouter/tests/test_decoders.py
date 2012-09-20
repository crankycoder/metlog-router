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
from metlogrouter.decoders import JSONDecoder
from gevent.queue import Empty, Queue
import gevent

import json


class TestDecoders(object):
    def setup(self):
        self.in_q = Queue()
        self.out_q = Queue()

    def test_json(self):
        MSG = {'foo': 'bar'}
        greenlets = []

        def insert_json_obj(in_q):
            in_q.put(json.dumps(MSG))

        def check_queue(output_queue):
            while True:
                try:
                    eq_(MSG, output_queue.get(block=False))
                    gevent.killall(greenlets)
                except Empty:
                    pass
                gevent.sleep(0)

        decoder = JSONDecoder()
        greenlets.append(gevent.spawn(decoder.start, self.in_q, self.out_q))
        greenlets.append(gevent.spawn(insert_json_obj, self.in_q))
        greenlets.append(gevent.spawn(check_queue, self.out_q))
        gevent.joinall(greenlets)
