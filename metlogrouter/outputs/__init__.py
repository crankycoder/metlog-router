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


class OutputQueue(object):
    """
    Wraps an output plugin with an 'inbox' queue and spins it up in a greenlet.
    """
    def __init__(self, plugin):
        self.plugin = plugin
        self.queue = Queue()

    def start(self):
        plugin = self.plugin
        in_queue = self.queue
        while True:
            try:
                msg = in_queue.get(timeout=0.01)
            except Empty:
                continue
            plugin.deliver(msg)
