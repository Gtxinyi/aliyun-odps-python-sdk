# Copyright 1999-2017 Alibaba Group Holding Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from odps.tests.core import TestBase, to_str
from odps.errors import ODPSError
from odps.compat import unittest
from odps.config import options
from odps.models import SQLTask, CupidTask, Task

try:
    import pytz
except ImportError:
    pytz = None


sql_template = '''<?xml version="1.0" encoding="utf-8"?>
<SQL>
  <Name>AnonymousSQLTask</Name>
  <Config>
    <Property>
      <Name>settings</Name>
      <Value>{"odps.sql.udf.strict.mode": "true"}</Value>
    </Property>
  </Config>
  <Query><![CDATA[%(sql)s;]]></Query>
</SQL>
'''

sql_tz_template = '''<?xml version="1.0" encoding="utf-8"?>
<SQL>
  <Name>AnonymousSQLTask</Name>
  <Config>
    <Property>
      <Name>settings</Name>
      <Value>{"odps.sql.timezone": "%(tz)s"}</Value>
    </Property>
  </Config>
  <Query><![CDATA[%(sql)s;]]></Query>
</SQL>
'''

cupid_template = '''<?xml version="1.0" encoding="utf-8"?>
<CUPID>
  <Name>task_1</Name>
  <Config>
    <Property>
      <Name>type</Name>
      <Value>cupid</Value>
    </Property>
    <Property>
      <Name>settings</Name>
      <Value>{"odps.cupid.wait.am.start.time": 600}</Value>
    </Property>
  </Config>
  <Plan><![CDATA[plan_text]]></Plan>
</CUPID>
'''


class Test(TestBase):
    def testTaskClassType(self):
        typed = Task(type='SQL', query='select * from dual')
        self.assertIsInstance(typed, SQLTask)

        unknown_typed = Task(type='UnknownType')
        self.assertIs(type(unknown_typed), Task)
        self.assertRaises(ODPSError, lambda: unknown_typed.serialize())

        untyped = Task()
        self.assertIs(type(untyped), Task)
        self.assertRaises(ODPSError, lambda: untyped.serialize())

    def testSQLTaskToXML(self):
        query = 'select * from dual'

        task = SQLTask(query=query)
        to_xml = task.serialize()
        right_xml = sql_template % {'sql': query}

        self.assertEqual(to_str(to_xml), to_str(right_xml))

        task = Task.parse(None, to_xml)
        self.assertIsInstance(task, SQLTask)

    @unittest.skipIf(pytz is None, 'pytz not installed')
    def testSQLTaskToXMLTimezone(self):
        from odps.lib import tzlocal
        query = 'select * from dual'

        try:
            options.local_timezone = True
            local_zone_name = tzlocal.get_localzone().zone
            task = SQLTask(query=query)
            task.update_sql_settings()
            to_xml = task.serialize()
            right_xml = sql_tz_template % {'sql': query, 'tz': local_zone_name}

            self.assertEqual(to_str(to_xml), to_str(right_xml))

            options.local_timezone = False
            task = SQLTask(query=query)
            task.update_sql_settings()
            to_xml = task.serialize()
            right_xml = sql_tz_template % {'sql': query, 'tz': 'Etc/GMT'}

            self.assertEqual(to_str(to_xml), to_str(right_xml))

            options.local_timezone = pytz.timezone('Asia/Shanghai')
            task = SQLTask(query=query)
            task.update_sql_settings()
            to_xml = task.serialize()
            right_xml = sql_tz_template % {'sql': query, 'tz': options.local_timezone.zone}

            self.assertEqual(to_str(to_xml), to_str(right_xml))
        finally:
            options.local_timezone = None

    def testCupidTaskToXML(self):
        task = CupidTask('task_1', 'plan_text', {'odps.cupid.wait.am.start.time': 600})
        to_xml = task.serialize()
        right_xml = cupid_template

        self.assertEqual(to_str(to_xml), to_str(right_xml))

        task = Task.parse(None, to_xml)
        self.assertIsInstance(task, CupidTask)


if __name__ == '__main__':
    unittest.main()
