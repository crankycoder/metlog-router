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
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from __future__ import absolute_import

from types import StringTypes

from raven import Client


class RavenOutput(object):
    """
    This output plugin talks to Sentry servers
    """
    def __init__(self, name, uri):
        self.name = name

        if isinstance(uri, StringTypes):
            uri = [uri]
        self.clients = [Client(u) for u in uri]

    def deliver(self, msg):
        for client in self.clients:
            client.send(msg['payload'])
