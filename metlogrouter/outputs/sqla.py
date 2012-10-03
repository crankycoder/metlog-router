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
from __future__ import absolute_import

from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime
import dateutil.parser

try:
    import simplejson as json
except ImportError:
    import json  # NOQA


# This tells the output plugin to take the `name` value that is embedded in the
# `fields` dictionary for timer and counter messages and to store it in the
# `field1` field on the SQL database side.
DEFAULT_FIELDSMAP = {'timer': {'name': 1},
                     'counter': {'name': 1},
                     }

metadata = MetaData()
messages = Table('messages', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('type', String, nullable=False),
                 Column('timestamp', DateTime, nullable=False),
                 Column('severity', Integer, nullable=False),
                 Column('hostname', String, nullable=False),
                 Column('pid', Integer, nullable=False),
                 Column('logger', String, nullable=False),
                 Column('payload', String),
                 Column('env_version', String, nullable=False),
                 Column('fields', String),
                 Column('field1', String),
                 Column('field2', String),
                 Column('field3', String),
                 Column('field4', String),
                 )


class SqlAlchemyOutput(object):
    """
    Store messages in an RDBMS using SqlAlchemy.
    """
    def __init__(self, engine, fieldsmap=None):
        """
        NOTE: `engine` must be using a gevent-safe db connector.
        """
        self.connection = engine.connect()
        self.fieldsmap = (fieldsmap if fieldsmap is not None
                          else DEFAULT_FIELDSMAP)
        metadata.create_all(engine)

    def deliver(self, msg):
        conn = self.connection
        fieldsmap = self.fieldsmap
        msgtype = msg['type']
        ins_kwargs = msg.copy()
        fields = ins_kwargs.get('fields', None)
        if fields:
            if msgtype in fieldsmap:
                # this type *does* store a field value in a fieldN column
                typemap = fieldsmap[msgtype]
                for fieldname, fieldnumber in typemap.items():
                    value = fields.get(fieldname)
                    ins_kwargs['field%d' % fieldnumber] = value
            ins_kwargs['fields'] = json.dumps(ins_kwargs['fields'])
        elif 'fields' in ins_kwargs:
            del ins_kwargs['fields']
        ins_kwargs['timestamp'] = dateutil.parser.parse(msg['timestamp'])
        ins_kwargs['hostname'] = ins_kwargs.pop('metlog_hostname')
        ins_kwargs['pid'] = ins_kwargs.pop('metlog_pid')

        insert = messages.insert()
        conn.execute(insert, **ins_kwargs)
