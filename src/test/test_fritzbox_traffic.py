#!/usr/bin/env python3
"""
  Unit tests for traffic module
"""

from unittest.mock import Mock
import unittest
import sys
from fritzbox_traffic import FritzboxTraffic

def get_fritzstatus_mock() -> Mock:
  mock_fritzstatus = Mock()
  mock_fritzstatus.max_bit_rate = [182, 1]
  mock_fritzstatus.transmission_rate = [1024, 4373]

  return mock_fritzstatus

class TestFritzboxTraffic(unittest.TestCase):
  maxDiff = None

  def test_config(self):
    traffic = FritzboxTraffic(get_fritzstatus_mock())
    traffic.print_config()

    # pylint: disable=no-member
    output = sys.stdout.getvalue().strip()
    self.assertEqual(output, """graph_title WAN traffic
graph_args --base 1000
graph_vlabel bit in (-) / out (+) per ${graph_period}
graph_category network
graph_order down up maxdown maxup
down.label received
down.type DERIVE
down.graph no
down.cdef down,8,*
down.min 0
down.max 1
up.label bps
up.type DERIVE
up.draw LINE
up.cdef up,8,*
up.min 0
up.max 182
up.negative down
up.info Traffic of the WAN interface.
maxdown.label received
maxdown.type GAUGE
maxdown.graph no
maxup.label MAX
maxup.type GAUGE
maxup.negative maxdown
maxup.draw LINE1
maxup.info Maximum speed of the WAN interface.""")

  def test_traffic(self):
    traffic = FritzboxTraffic(get_fritzstatus_mock())
    traffic.print_traffic()

    # pylint: disable=no-member
    output = sys.stdout.getvalue().strip()
    self.assertEqual(output, """down.value 4373
up.value 1024
maxdown.value 1
maxup.value 182""")

if __name__ == '__main__':
  unittest.main(module=__name__, buffer=True, exit=False)
