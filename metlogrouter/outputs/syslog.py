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

import syslog
import threading


class SyslogOutput(object):
    """
    Simple UDP socket listener.

    Syslog messages are expected to be formatted as
    """
    def __init__(self):
        self._LOG_OPENED = None
        self._log_lock = threading.RLock()

    def deliver(self, msg):
        with self._log_lock:
            ident = msg['ident'].encode('utf8')
            logopt = msg['logopt']
            facility = msg['facility']
            priority = msg['priority']
            syslog_msg = msg['msg'].encode('utf8')

            if self._LOG_OPENED != (ident, logopt, facility):
                self._LOG_OPENED = ident, logopt, facility
                syslog.openlog(ident, logopt, facility)

            if isinstance(syslog_msg, unicode):
                syslog_msg = syslog_msg.encode('utf-8')
            syslog.syslog(priority, syslog_msg)
