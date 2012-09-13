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
try:
    import simplejson as json
except ImportError:
    import json  # NOQA


class EchoFilter(object):
    def __init__(self, stream):
        self.stream = stream

    def filter_msg(self, msg):
        msg_json = json.dumps(msg)
        self.stream.write(msg_json + '\n')
        self.stream.flush()
        return (msg, None)


class SendToStdoutFilter(object):
    def filter_msg(self, msg):
        return (msg, 'stdout')
