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
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
import gevent
from gevent.queue import Empty, Queue

try:
    import simplejson as json
except ImportError:
    import json  # NOQA


class JSONDecoder(object):
    def __init__(self):
        self.queue = Queue()

    def start(self, out_queue):
        in_queue = self.queue  # local var lookup is faster
        while True:
            try:
                obj = in_queue.get(timeout=0.1)
            except Empty:
                continue
            out_queue.put(json.loads(obj))
            gevent.sleep(0)
