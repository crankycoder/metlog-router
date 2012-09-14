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
from gevent.queue import Empty, Queue
from types import StringTypes
import gevent


def run(inputs=None, decoders=None, filters=None, outputs=None,
        forced_outputs=None):
    """
    Bootstrap the entire router.
    """
    greenlets = []
    input_queue = Queue()

    object_queue = Queue()

    inputs, decoders, filters, outputs, forced_outputs = \
            [(i or [])
                for i in (inputs, decoders, filters, outputs, forced_outputs)]
    outputs_map = dict()
    for output_plugin in outputs:
        outputs_map[output_plugin.name] = output_plugin

    for input_plugin in inputs:
        # inputs must not block!
        greenlets.append(gevent.spawn(input_plugin.start, input_queue))

    for decode_plugin in decoders:
        greenlets.append(gevent.spawn(decode_plugin.start,
            input_queue, object_queue))

    def filter_processor():
        """
        Get messages from the input queue and run them through the filters.
        """
        while True:
            try:
                msg = object_queue.get(timeout=0.01)
            except Empty:
                continue

            outputs_to_use = set(forced_outputs)
            for filter_plugin in filters:
                msg, added_outputs = filter_plugin.filter_msg(msg)
                if added_outputs:
                    outputs_to_use.update([name for name in added_outputs])

            for output_name in outputs_to_use:
                output_plugin = outputs_map[output_name]
                output_plugin.deliver(msg)

            gevent.sleep(0)

    greenlets.append(gevent.spawn(filter_processor))
    gevent.joinall(greenlets)
