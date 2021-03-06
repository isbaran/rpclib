#!/usr/bin/env python
#
# rpclib - Copyright (C) Rpclib contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import datetime
import unittest

from lxml import etree

from rpclib.model.complex import Array
from rpclib.model.primitive import Boolean
from rpclib.model.primitive import DateTime
from rpclib.model.primitive import Duration
from rpclib.model.primitive import Float
from rpclib.model.primitive import Integer
from rpclib.model.base import Null
from rpclib.model.primitive import String
from rpclib.protocol.soap import namespace as ns

from rpclib.util.duration import XmlDuration

ns_test = 'test_namespace'

class TestPrimitive(unittest.TestCase):
    def test_string(self):
        s = String()
        element = etree.Element('test')
        String.to_parent_element('value', ns_test, element)
        element=element[0]
        
        self.assertEquals(element.text, 'value')
        value = String.from_xml(element)
        self.assertEquals(value, 'value')

    def test_datetime(self):
        d = DateTime()
        n = datetime.datetime.now()

        element = etree.Element('test')
        DateTime.to_parent_element(n, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, n.isoformat())
        dt = DateTime.from_xml(element)
        self.assertEquals(n, dt)
    
    def test_duration_timedelta(self):
        delta = datetime.timedelta(days=400, seconds=3672)

        element = etree.Element('test')
        Duration.to_parent_element(delta, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, 'P1Y1M5DT1H1M12S')
        du = Duration.from_xml(element)
        self.assertEquals(delta, du)

    def test_duration_xml_duration(self):
        dur = XmlDuration(years=1, months=1, days=5,
                          hours=1, minutes=1, seconds=12.0)
        dur2 = XmlDuration.from_string('P400DT3672S')
        self.assertEquals(dur.as_timedelta(), dur2.as_timedelta())

        element = etree.Element('test')
        Duration.to_parent_element(dur, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, 'P1Y1M5DT1H1M12S')
        du = Duration.from_xml(element)
        self.assertEquals(dur.as_timedelta(), du)

    def test_utcdatetime(self):
        datestring = '2007-05-15T13:40:44Z'
        e = etree.Element('test')
        e.text = datestring

        dt = DateTime.from_xml(e)

        self.assertEquals(dt.year, 2007)
        self.assertEquals(dt.month, 5)
        self.assertEquals(dt.day, 15)

        datestring = '2007-05-15T13:40:44.003Z'
        e = etree.Element('test')
        e.text = datestring

        dt = DateTime.from_xml(e)

        self.assertEquals(dt.year, 2007)
        self.assertEquals(dt.month, 5)
        self.assertEquals(dt.day, 15)

    def test_integer(self):
        i = 12
        integer = Integer()

        element = etree.Element('test')
        Integer.to_parent_element(i, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, '12')
        value = integer.from_xml(element)
        self.assertEquals(value, i)

    def test_large_integer(self):
        i = 128375873458473
        integer = Integer()

        element = etree.Element('test')
        Integer.to_parent_element(i, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, '128375873458473')
        value = integer.from_xml(element)
        self.assertEquals(value, i)

    def test_float(self):
        f = 1.22255645

        element = etree.Element('test')
        Float.to_parent_element(f, ns_test, element)
        element = element[0]

        self.assertEquals(element.text, repr(f))

        f2 = Float.from_xml(element)
        self.assertEquals(f2, f)

    def test_array(self):
        type = Array(String)
        type.resolve_namespace(type,"zbank")

        values = ['a', 'b', 'c', 'd', 'e', 'f']

        element = etree.Element('test')
        type.to_parent_element(values, ns_test, element)
        element = element[0]

        self.assertEquals(len(values), len(element.getchildren()))

        values2 = type.from_xml(element)
        self.assertEquals(values[3], values2[3])

    def test_array_empty(self):
        type = Array(String)
        type.resolve_namespace(type,"zbank")

        values = []

        element = etree.Element('test')
        type.to_parent_element(values, ns_test, element)
        element = element[0]

        self.assertEquals(len(values), len(element.getchildren()))

        values2 = type.from_xml(element)
        self.assertEquals(len(values2), 0)

    def test_unicode(self):
        s = u'\x34\x55\x65\x34'
        self.assertEquals(4, len(s))
        element = etree.Element('test')
        String.to_parent_element(s, 'test_ns', element)
        element = element[0]
        value = String.from_xml(element)
        self.assertEquals(value, s)

    def test_null(self):
        element = etree.Element('test')
        Null.to_parent_element('doesnt matter', ns_test, element)
        element = element[0]
        self.assertTrue( bool(element.get('{%s}nil' % ns.xsi)) )
        value = Null.from_xml(element)
        self.assertEquals(None, value)

    def test_boolean(self):
        b = etree.Element('test')
        Boolean.to_parent_element(True, ns_test, b)
        b = b[0]
        self.assertEquals('true', b.text)

        b = etree.Element('test')
        Boolean.to_parent_element(0, ns_test, b)
        b = b[0]
        self.assertEquals('false', b.text)

        b = etree.Element('test')
        Boolean.to_parent_element(1, ns_test, b)
        b = b[0]
        self.assertEquals('true', b.text)

        b = Boolean.from_xml(b)
        self.assertEquals(b, True)

        b = etree.Element('test')
        Boolean.to_parent_element(False, ns_test, b)
        b = b[0]
        self.assertEquals('false', b.text)

        b = Boolean.from_xml(b)
        self.assertEquals(b, False)

        b = etree.Element('test')
        Boolean.to_parent_element(None, ns_test, b)
        b = b[0]
        self.assertEquals('true', b.get('{%s}nil' % ns.xsi))

        b = Boolean.from_xml(b)
        self.assertEquals(b, None)

if __name__ == '__main__':
    unittest.main()
