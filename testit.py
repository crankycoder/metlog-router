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
"""Metlog Router testit script

Usage:
  testit.py [--fd=<file descriptor>]

Options:
  --fd=<file descriptor>      UDP listener socket file descriptor

"""
from docopt import docopt
from metlogrouter.filters import NamedOutputFilter
from metlogrouter.inputs import UdpInput
from metlogrouter.outputs.debug import CounterOutput, StreamOutput
from metlogrouter.runner import run
import sys

arguments = docopt(__doc__)
if '--fd' in arguments:
    udpinput = UdpInput(fd=int(arguments['--fd']))
else:
    udpinput = UdpInput(port=5565)

inputs = {'udp': udpinput,
          }

# filters are used to tag messagse to match a particular key in the
# outputs dictionary to route messages to a final destination
filters = [NamedOutputFilter('counts')]
outputs = {'counts': CounterOutput(100),
           'stdout': StreamOutput(sys.stdout),
           }

config = {'inputs': inputs,
          'filters': filters,
          'outputs': outputs,
          }

run(config)
