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
from metlogrouter.decoders import JSONDecoder
import gevent
import re
import sys


def run(config):
    """
    Bootstrap the entire router.
    """
    greenlets = []
    input_queue = Queue()
    decoded_queue = Queue()

    inputs = config.get('inputs', dict())
    decoders = config.get('decoders', dict())
    default_decoder = config.get('default_decoder')
    filters = config.get('filters', list())
    outputs = config.get('outputs', dict())
    forced_outputs = config.get('forced_outputs', list())

    for input_plugin in inputs.values():
        # inputs must only block greenlets, *not* the entire thread
        greenlets.append(gevent.spawn(input_plugin.start, input_queue))
        print unicode(input_plugin)

    if not decoders:
        decoders = {'json': JSONDecoder()}
    if default_decoder is None:
        if len(decoders) == 1:
            default_decoder = decoders.keys()[0]
        else:
            raise ValueError('No default decoder specified.')
    elif default_decoder not in decoders:
        raise ValueError('Specified default decoder does not exist: %s'
                         % default_decoder)

    for decode_plugin in decoders.values():
        greenlets.append(gevent.spawn(decode_plugin.start, decoded_queue))

    decoder_names = '|'.join(decoders.keys())
    decoders_regex = '\A::(%s)::' % decoder_names
    decoders_regex = re.compile(decoders_regex)

    def input_processor():
        """
        Get messages from the input queue, determine the appropriate decoder to
        use, and add the message to that decoder's queue.
        """
        while True:
            try:
                msg = input_queue.get(timeout=0.1)
            except Empty:
                continue

            decoder_name = default_decoder
            match = decoders_regex.match(msg)
            if match is not None:
                decoder_name = match.groups()[0]
                msg = msg[match.end():]
            decoder = decoders.get(decoder_name)
            if decoder is None:
                sys.stderr.write('Decoder not available: %s\n' % decoder_name)
                sys.stderr.flush()
                gevent.sleep(0)
                continue

            decoder.queue.put(msg)
            gevent.sleep(0)

    greenlets.append(gevent.spawn(input_processor))

    def filter_processor():
        """
        Get messages from the decoded queue and run them through the filters.
        """
        while True:
            try:
                msg = decoded_queue.get(timeout=0.1)
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
