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
from gevent.queue import Empty

try:
    import simplejson as json
except ImportError:
    import json  # NOQA


class JSONDecoder(object):

    def start(self, in_q, out_q):
        self.in_q = in_q
        self.out_q = out_q
        while True:
            try:
                obj = self.in_q.get(timeout=0.1)
            except Empty:
                gevent.sleep(0)
                continue
            self.out_q.put(json.loads(obj))
            gevent.sleep(0)
