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
import json
import os
import os.path


VALID_FMTS = ('json', 'text')


class InvalidFileFormat(NotImplementedError):
    pass


class ArgumentError(StandardError):
    pass


class FileOutput(object):
    """
    This just writes some text to a file.

    We also handle two special messages to suspend and open
    files when logs are rotated.  These can be used during a logrotate
    prerotate and postrotate clauses to temporarily suspend file i/o
    while a file rotation is occuring.
    """

    def __init__(self, path, output_fmt='json',
            keypath=None, prefix_ts=False):

        if output_fmt not in VALID_FMTS:
            msg = "%s output format is not implemented" % output_fmt
            raise InvalidFileFormat(msg)

        self.output_fmt = output_fmt

        self.output_method = {'json': self._output_json,
                             'text': self._output_text}.get(self.output_fmt)

        if os.path.isdir(path):
            raise ArgumentError("Output path must be a file")

        self.path = path

        # Create the directory if it doesn't exist
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if keypath:
            self.keypath = keypath.split("/")
        else:
            self.keypath = []

        self.prefix_ts = prefix_ts

        self.output_file = None
        self.open(None)

        self.meta_payloads = {
                'metlog::file::open': self.open,
                'metlog::file::close': self.close,
                }

    def deliver(self, msg):
        self.meta_payloads.get(msg['fields'].get('meta', None),
                self.output_method)(msg)

    def open(self, ignored):
        if self.output_file != None:
            raise IOError("%s is already open and in use" % self.path)
        self.output_file = open(self.path, 'ab')

    def close(self, ignored):
        if self.output_file is None:
            msg = "File [%s] is not currently open" % self.path
            raise IOError(msg)
        self.output_file.close()
        self.output_file = None

    def _output_json(self, msg):
        value = msg
        for segment in self.keypath:
            value = value.get(segment, None)
            if value is None:
                # Ran off the end of the dictionary, just skip to the
                # next item
                return
        self.output_file.write(json.dumps(value))

    def _output_text(self, msg):
        value = msg
        for segment in self.keypath:
            value = value.get(segment, None)
            if value is None:
                # Ran off the end of the dictionary, just skip to the
                # next item
                return

        output_txt = str(value)

        if self.prefix_ts:
            ts = msg['timestamp'] + ' '
        else:
            ts = ''

        self.output_file.write("%s%s" % (ts, output_txt))
