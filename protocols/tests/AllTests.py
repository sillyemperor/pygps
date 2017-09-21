from ..longhan import Longhan16m
from ..xinan import Xinan

import unittest
from ..result import Location, HeartBeat
import binascii

class AllTests(unittest.TestCase):

    def test_Xinan(self):
        s = '292980002810899f2d141015112501030183471200539100000000f8000442ffff5400001e000000000000450d'
        proc = Xinan()
        result, response = proc.on_message(binascii.a2b_hex(s))

    def test_Longhan16m(self):
        s = '2929800032150b1a94170921213448028412051214493700000102fc15480aaffddff8001e00000000000000080010013121112620740d'
        print len(s)
        proc = Longhan16m()
        result, response = proc.on_message(binascii.a2b_hex(s))
        self.assertEqual('2929210005748017C70D', response)
        self.assertIsInstance(result, Location)
        self.assertTrue(result.jit)

        s = '29298e001b15321ad71709212134000284140112145339000000008b0001200d'
        result, response = proc.on_message(binascii.a2b_hex(s))
        self.assertFalse(result.jit)

        s = '2929b10011150b1a940600080010013121112620280d'
        print len(s)
        result, response = proc.on_message(binascii.a2b_hex(s))
        self.assertIsInstance(result, HeartBeat)

        s = '292980002815321ae3170921213338028506581210761700000000ff15d75ee7fd7f0003c0078000010802b0d0'
        print len(s)
        result, response = proc.on_message(binascii.unhexlify(s.strip()))
        print result
        self.assertIsInstance(result, Location)
