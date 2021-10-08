#!/usr/bin/env python3
"""
  Unit tests for dsl module
"""

from unittest.mock import Mock
import os
import unittest
import sys
from fritzbox_dsl import FritzboxDsl
from FritzboxInterface import FritzboxInterface
from base_test_case import BaseTestCase

class TestFritzboxDsl(BaseTestCase):
  @unittest.mock.patch.dict(os.environ, {
    "dsl_modes": "INVALID"
  })
  def test_config_with_invalid_modes_only(self):
    dsl = FritzboxDsl(self._get_interface_mock())
    dsl.print_config()

    # pylint: disable=no-member
    output = sys.stdout.getvalue().strip()
    self.assertEqual(output, "")

  @unittest.mock.patch.dict(os.environ, {
    "dsl_modes": "capacity snr damping errors crc INVALID"
  })
  def test_config(self):
    dsl = FritzboxDsl(self._get_interface_mock())
    dsl.print_config()

    # pylint: disable=no-member
    output = sys.stdout.getvalue().strip()
    self.assertEqual(output, """multigraph dsl_capacity
graph_title Link Capacity
graph_vlabel bit/s
graph_args --lower-limit 0
graph_category network
recv.label receive
recv.type GAUGE
recv.graph LINE1
recv.min 0
recv.cdef recv,1000,*
recv.warning 61732000
send.label send
send.type GAUGE
send.graph LINE1
send.min 0
send.cdef send,1000,*
send.warning 12443000
multigraph dsl_snr
graph_title Signal-to-Noise Ratio
graph_vlabel dB
graph_args --lower-limit 0
graph_category network
recv.label receive
recv.type GAUGE
recv.graph LINE1
recv.min 0
send.label send
send.type GAUGE
send.graph LINE1
send.min 0
multigraph dsl_damping
graph_title Line Loss
graph_vlabel dB
graph_args --lower-limit 0
graph_category network
recv.label receive
recv.type GAUGE
recv.graph LINE1
recv.min 0
send.label send
send.type GAUGE
send.graph LINE1
send.min 0
multigraph dsl_crc
graph_title Checksum Errors
graph_vlabel n
graph_args --lower-limit 0
graph_category network
recv.label receive
recv.type GAUGE
recv.graph LINE1
recv.min 0
send.label send
send.type GAUGE
send.graph LINE1
send.min 0
multigraph dsl_errors
graph_title Transmission Errors
graph_vlabel s
graph_args --lower-limit 0
graph_category network
graph_order es_recv es_send ses_recv ses_send
es_recv.label receive errored
es_recv.type DERIVE
es_recv.graph LINE1
es_recv.min 0
es_recv.warning 1
es_send.label send errored
es_send.type DERIVE
es_send.graph LINE1
es_send.min 0
es_send.warning 1
ses_recv.label receive severely errored
ses_recv.type DERIVE
ses_recv.graph LINE1
ses_recv.min 0
ses_recv.warning 1
ses_send.label send severely errored
ses_send.type DERIVE
ses_send.graph LINE1
ses_send.min 0
ses_send.warning 1""")

  def test_print_dsl_stats(self):
    dsl = FritzboxDsl(self._get_interface_mock())
    dsl.print_dsl_stats()

    # pylint: disable=no-member
    output = sys.stdout.getvalue().strip()
    self.assertEqual(output, """multigraph dsl_capacity
recv.value 139083
send.value 47102
multigraph dsl_snr
recv.value 28
send.value 31
multigraph dsl_damping
recv.value 6
send.value 4
multigraph dsl_errors
es_recv.value 0
es_send.value 0
ses_recv.value 0
ses_send.value 0
multigraph dsl_crc
recv.value 0
send.value 0""")

if __name__ == '__main__':
  suite = unittest.TestSuite()
  for fritzbox_model in ['7590-7.28']:
    suite.addTest(BaseTestCase.parametrize(TestFritzboxDsl, param=fritzbox_model))

  unittest.TextTestRunner(verbosity=2, buffer=True).run(suite)
