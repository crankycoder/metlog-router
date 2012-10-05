#!/usr/bin/env python
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
from docopt import docopt
from metlogrouter.decoders.msgpack import MsgPackDecoder
from metlogrouter.filters import NamedOutputFilter
from metlogrouter.inputs import UdpInput
from metlogrouter.outputs.debug import CounterOutput, StreamOutput
from metlogrouter.runner import run
import sys

mlrouterd_doc = """mlrouterd: Metlog Router process launcher

Usage:
  mlrouterd [--fd=<file descriptor>] [--sqlurl=<URL>] [--decoder=json|msgpack]

Options:
  --fd=<file descriptor>      UDP listener socket file descriptor
  --sqlurl=<URL>              SQLAlchemy connection string
  --decoder=json|msgpack      Decoder to use
"""


def mlrouterd():
    arguments = docopt(mlrouterd_doc)
    if arguments.get('--fd'):
        udpinput = UdpInput(fd=int(arguments['--fd']))
    else:
        udpinput = UdpInput(port=5565)

    inputs = {'udp': udpinput,
              }

    # filters are used to tag messages to match a particular key in the outputs
    # dictionary to route messages to a final destination
    filters = [NamedOutputFilter(['counts'])]
    outputs = {'counts': CounterOutput(),
               'stdout': StreamOutput(sys.stdout),
               }

    if arguments.get('--sqlurl'):
        from metlogrouter.outputs.sqla import SqlAlchemyOutput
        from sqlalchemy import create_engine
        engine = create_engine(arguments['--sqlurl'])
        outputs['sqla'] = SqlAlchemyOutput(engine)
        filters = [NamedOutputFilter(['counts', 'sqla'])]

    config = {'inputs': inputs,
              'filters': filters,
              'outputs': outputs,
              }

    if arguments.get('--decoder'):
        decoder = arguments['--decoder']
        if decoder == 'msgpack':
            config['decoders'] = {'msgpack': MsgPackDecoder()}
            config['default_decoder'] = 'msgpack'
        elif decoder != 'json':
            raise ValueError('No "%s" decoder exists' % str(decoder))

    run(config)
