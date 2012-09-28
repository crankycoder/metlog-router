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
from nose.tools import eq_
from metlogrouter.filters import NamedOutputFilter, SendToStdoutFilter


class TestFilters(object):
    def test_named_filter(self):
        tags = ['foo']

        filter = NamedOutputFilter(tags)
        eq_(('foo', set(tags)), filter.filter_msg('foo', set()))

    def test_stdout_filter(self):
        filter = SendToStdoutFilter()
        eq_(('foo', set(['stdout'])), filter.filter_msg('foo', set()))
