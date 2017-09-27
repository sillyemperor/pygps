import unittest
import binascii
import datetime

from ..longhan import Longhan16m
from ..xinan import Xinan
from ..result import Location, HeartBeat


class AllTestCase(unittest.TestCase):

    def test_Xinan(self):
        s = '292980002810899f2d141015112501030183471200539100000000f8000442ffff5400001e000000000000450d'
        proc = Xinan()
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        self.assertEqual(result.altitude, 0)
        self.assertEqual(result.bearing, 0),
        self.assertEqual(result.imei, '13616093145'),
        self.assertEqual(result.jit, True),
        self.assertEqual(result.lat, 30.305783333333334),
        self.assertEqual(result.lng, 120.08985),
        self.assertEqual(result.speed, 0.0),
        self.assertEqual(result.time, datetime.datetime(2014, 10, 15, 11, 25, 1))

        s = '29298e0028348ace2a170927225529030090261215977000000000f8b0c8ab7fffc0000000000000000000a50d'
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        print result, response, input_data

        s = '29298000281086985400000014522400000000000000000000000078fbbec37ffc1900001e000000000000ea0d'
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        print result, response, input_data

        s = '2929b10007348ace0d0cc70d'
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        print result, response, input_data

    def test_Longhan16m(self):
        s = '2929800032150b1a94170921213448028412051214493700000102fc15480aaffddff8001e00000000000000080010013121112620740d'
        proc = Longhan16m()
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        self.assertEqual('2929210005748017C70D', response)
        self.assertTrue(result.jit)
        self.assertEqual(result.altitude, 0),
        self.assertEqual(result.bearing, 102),
        self.assertEqual(result.imei, '13121112620')
        self.assertEqual(result.lat, 28.68675)
        self.assertEqual(result.lng, 121.74895)
        self.assertEqual(result.speed, 0.0)
        self.assertEqual(result.time, datetime.datetime(2017, 9, 21, 21, 34, 48))

        s = '29298e001b15321ad71709212134000284140112145339000000008b0001200d'
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        self.assertFalse(result.jit)
        self.assertEqual(result.altitude, 0)
        self.assertEqual(result.bearing, 0)
        self.assertEqual(result.imei, '13121502687')
        self.assertEqual(result.lat, 28.690016666666665)
        self.assertEqual(result.lng, 121.75565)
        self.assertEqual(result.speed, 0.0)
        self.assertEqual(result.time, datetime.datetime(2017, 9, 21, 21, 34))

        s = '2929b10011150b1a940600080010013121112620280d'
        result, response, input_data = proc.on_message(binascii.a2b_hex(s))
        self.assertIsInstance(result, HeartBeat)

        s = '292980002815321ae3170921213338028506581210761700000000ff15d75ee7fd7f0003c0078000010802b0d0'
        result, response, input_data = proc.on_message(binascii.unhexlify(s.strip()))
        self.assertIsInstance(result, Location)
        self.assertEqual(result.altitude, 0)
        self.assertEqual(result.bearing, 0)
        self.assertEqual(result.imei, '13121502699')
        self.assertEqual(result.jit, True)
        self.assertEqual(result.lat, 28.8443)
        self.assertEqual(result.lng, 121.12695)
        self.assertEqual(result.speed, 0.0)
        self.assertEqual(result.time, datetime.datetime(2017, 9, 21, 21, 33, 38))
