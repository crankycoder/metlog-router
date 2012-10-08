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
from __future__ import absolute_import

from gevent.queue import Empty, Queue
import gevent
import msgpack


class MsgPackDecoder(object):
    def __init__(self):
        self.queue = Queue()

    def start(self, out_queue):
        in_queue = self.queue  # local var lookup is faster
        while True:
            try:
                obj = in_queue.get(timeout=0.01)
            except Empty:
                continue
            out_queue.put(msgpack.loads(obj))
            gevent.sleep(0)
