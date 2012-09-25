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
#   Rob Miller (rmiller@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from __future__ import absolute_import

from metlogrouter.outputs.fileoutput import FileOutput
from metlogrouter.outputs.fileoutput import InvalidFileFormat
from mock import patch
from nose import SkipTest
from nose.tools import eq_, raises, assert_raises
import json
import tempfile


try:
    from metlogrouter.outputs.statsd import StatsdOutput
except ImportError:
    StatsdOutput = None  # NOQA


class TestStatsd(object):
    def setup(self):
        if StatsdOutput is None:
            raise SkipTest
        self.client_proxy = StatsdOutput('statsd', 'localhost')
        self.client = self.client_proxy.clients[0]

    def test_statsd_incr(self):
        ctx = patch.object(self.client, 'incr')
        with ctx:
            self.client_proxy.deliver({'fields': {'name': 'testing.statsd',
                                       'type': 'counter',
                                       'rate': '1'},
                            'payload': 2})

            method = self.client.incr
            eq_(len(method.call_args_list), 1)

            call_msg = method.call_args_list[0]
            eq_(call_msg[0], ('testing.statsd', 2.0, 1.0))

    def test_statsd_timing(self):
        ctx = patch.object(self.client, 'timing')
        with ctx:
            self.client_proxy.deliver({'fields': {'name': 'testing.statsd',
                                       'type': 'timer',
                                       'rate': '4'},
                            'payload': 5})

            method = self.client.timing
            eq_(len(method.call_args_list), 1)

            call_msg = method.call_args_list[0]
            eq_(call_msg[0], ('testing.statsd', 5.0, 4.0))

    def test_statsd_gauge(self):
        ctx = patch.object(self.client, 'gauge')
        with ctx:
            self.client_proxy.deliver({'fields': {'name': 'testing.statsd',
                                       'type': 'gauge',
                                       'rate': '8'},
                            'payload': 3})

            method = self.client.gauge
            eq_(len(method.call_args_list), 1)

            call_msg = method.call_args_list[0]
            eq_(call_msg[0], ('testing.statsd', 3.0, 8.0))


try:
    from metlogrouter.outputs.raven import RavenOutput
except ImportError:
    RavenOutput = None  # NOQA


class TestRaven(object):
    def setup(self):
        if RavenOutput is None:
            raise SkipTest
        self.client_proxy = RavenOutput('test_raven',
                "http://user:password@localhost:9000/1")
        self.client = self.client_proxy.clients[0]

    def test_sentry(self):
        ctx = patch.object(self.client, 'send')
        with ctx:
            self.client_proxy.deliver({'fields': {'name': 'testing.statsd',
                                       'type': 'gauge',
                                       'rate': '8'},
                            'payload': 'not_real_sentry_data'})

            method = self.client.send
            eq_(len(method.call_args_list), 1)

            call_msg = method.call_args_list[0]
            eq_(call_msg[0], ('not_real_sentry_data',))


class TestFile(object):
    def setup(self):
        fout = tempfile.NamedTemporaryFile(mode='ab', delete=True)
        self.temp_filename = fout.name
        fout.close()

    def test_file_write(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='text',
                keypath='fields/bar')
        ctx = patch.object(self.client, 'output_file')
        with ctx:
            obj = {'fields': {'bar': "This is a magic number: 42"}}
            self.client.deliver(obj)

            mock = self.client.output_file
            eq_(len(mock.method_calls), 1)

            eq_(mock.method_calls[0][1], ('This is a magic number: 42',))

    def test_keyed_json_write(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='json',
                keypath='fields/bar')
        ctx = patch.object(self.client, 'output_file')
        with ctx:
            obj = {'fields':
                    {'bar':
                    {'bad':
                    "This is a magic number: 42"}}}
            self.client.deliver(obj)

            mock = self.client.output_file
            eq_(len(mock.method_calls), 1)

            eq_(mock.method_calls[0][1],
                    ('{"bad": "This is a magic number: 42"}',))

    def test_json_output(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='json')
        ctx = patch.object(self.client, 'output_file')
        with ctx:
            obj = {'fields':
                    {'bar':
                    {'bad':
                    "This is a magic number: 42"}}}
            self.client.deliver(obj)

            mock = self.client.output_file
            eq_(len(mock.method_calls), 1)

            expected = json.dumps(obj)
            eq_(mock.method_calls[0][1], (expected,))

    def test_prefix_timestamps(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='text',
                keypath='fields/bar',
                prefix_ts=True)
        ctx = patch.object(self.client, 'output_file')
        with ctx:
            obj = {'timestamp': 'faketimestamp',
                   'fields': {'bar': "This is a magic number: 42"}}
            self.client.deliver(obj)

            mock = self.client.output_file
            eq_(len(mock.method_calls), 1)

            expected = ('faketimestamp This is a magic number: 42',)
            eq_(mock.method_calls[0][1], expected)

    def test_double_open(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='text',
                keypath='fields/bar',
                prefix_ts=True)

        obj = {'fields': {'meta': "metlog::file::open"}}

        # This should fail
        assert_raises(IOError, self.client.deliver, obj)

    def test_double_close(self):
        self.client = FileOutput(self.temp_filename,
                output_fmt='text',
                keypath='fields/bar',
                prefix_ts=True)
        obj = {'fields': {'meta': "metlog::file::close"}}

        # This should fail
        self.client.deliver(obj)
        assert_raises(IOError, self.client.deliver, obj)

    @raises(InvalidFileFormat)
    def test_invalid_format(self):
        FileOutput(self.temp_filename,
                output_fmt='bad_fmt',
                keypath='fields/bar')
