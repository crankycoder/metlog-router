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
from metlogrouter.filters import NamedOutputFilter

from metlogrouter.inputs import UdpInput
from metlogrouter.decoders import JSONDecoder
from metlogrouter.outputs import CounterOutput
from metlogrouter.runner import run

inputs = {'udp': UdpInput(port=5565)}
decoders = {'json': JSONDecoder()}
filters = [NamedOutputFilter('counts')]
outputs = {'counts': CounterOutput(100)}

config = {'inputs': inputs,
          'decoders': decoders,
          'filters': filters,
          'outputs': outputs,
          }
run(config)
