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
import gevent


def run(config):
    """
    Bootstrap the entire router.
    """
    greenlets = []
    input_queue = Queue()
    object_queue = Queue()

    inputs = config.get('inputs', dict())
    decoders = config.get('decoders', dict())
    filters = config.get('filters', list())
    outputs = config.get('outputs', dict())
    forced_outputs = config.get('forced_outputs', list())

    for input_plugin in inputs.values():
        # inputs must only block greenlets, *not* the entire thread
        greenlets.append(gevent.spawn(input_plugin.start, input_queue))
        print unicode(input_plugin)

    for decode_plugin in decoders.values():
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
                output_plugin = outputs[output_name]
                # TODO: the output plugins should pull explicitly from
                # a queue so that exceptions
                output_plugin.deliver(msg)

            gevent.sleep(0)

    greenlets.append(gevent.spawn(filter_processor))
    gevent.joinall(greenlets)
