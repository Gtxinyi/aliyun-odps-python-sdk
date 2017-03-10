#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import random
import time
from datetime import datetime
from decimal import Decimal
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

from odps.tests.core import TestBase as Base, to_str, tn, pandas_case
from odps import types
from odps.df.backends.frame import ResultFrame


class TestBase(Base):
    def _gen_random_bigint(self, value_range=None):
        return random.randint(*(value_range or types.bigint._bounds))

    def _gen_random_string(self, max_length=15):
        gen_letter = lambda: letters[random.randint(0, 51)]
        return to_str(''.join([gen_letter() for _ in range(random.randint(1, max_length))]))

    def _gen_random_double(self):
        return random.uniform(-2**32, 2**32)

    def _gen_random_datetime(self):
        dt = datetime.fromtimestamp(random.randint(0, int(time.time())))
        if dt.year >= 1986 or dt.year <= 1992:  # ignore years when daylight saving time is used
            return dt.replace(year=1996)
        else:
            return dt

    def _gen_random_boolean(self):
        return random.uniform(-1, 1) > 0

    def _gen_random_decimal(self):
        return Decimal(str(self._gen_random_double()))

    def _get_result(self, res):
        if isinstance(res, ResultFrame):
            res = res.values
        try:
            import pandas
            import numpy

            def conv(t):
                try:
                    if numpy.isnan(t):
                        return None
                except TypeError:
                    pass
                if isinstance(t, pandas.Timestamp):
                    t = t.to_pydatetime()
                elif pandas.isnull(t):
                    t = None
                return t

            if isinstance(res, pandas.DataFrame):
                return [list(conv(i) for i in it) for it in res.values]
            else:
                return res
        except ImportError:
            return res

    def assertListAlmostEqual(self, first, second, **kw):
        self.assertEqual(len(first), len(second))
        only_float = kw.pop('only_float', True)
        for f, s in zip(first, second):
            if only_float:
                self.assertAlmostEqual(f, s, **kw)
            else:
                if isinstance(f, float) and isinstance(s, float):
                    self.assertAlmostEqual(f, s, **kw)
                elif isinstance(f, list) and isinstance(s, list):
                    self.assertListAlmostEqual(f, s, only_float=True, **kw)
                else:
                    self.assertEqual(f, s)


__all__ = ['TestBase', 'to_str', 'tn', 'pandas_case']
