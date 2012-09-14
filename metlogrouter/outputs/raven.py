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

from types import StringTypes


class RavenOutput(object):
    """
    This output plugin talks to Sentry servers
    """
    def __init__(self, name, uri):
        self.name = name

        if isinstance(uri, StringTypes):
            uri = [uri]
        self.uri = uri

    def deliver(self, msg):
        # TODO: take a look at logstash-metlog/logstash/outputs/sentry
        # and hook appropriate parts from actual raven client
        pass


