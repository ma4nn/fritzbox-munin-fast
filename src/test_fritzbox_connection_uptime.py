#!/usr/bin/env python3
"""
  Unit tests for connection uptime module
"""

from unittest.mock import MagicMock
from fritzbox_connection_uptime import FritzboxConnectionUptime

def get_fritzstatus_mock() -> MagicMock:
  mock_fritzstatus = MagicMock()
  mock_fritzstatus.external_ip = '127.0.0.1'
  mock_fritzstatus.external_ipv6 = '0000::0000::0000::0000'
  mock_fritzstatus.connection_uptime = 18720
  mock_fritzstatus.uptime = mock_fritzstatus.connection_uptime

  return mock_fritzstatus

class TestFritzboxConnectionUptime():
  def test_config(self, capsys):
    uptime = FritzboxConnectionUptime(get_fritzstatus_mock())
    uptime.print_config()

    assert capsys.readouterr().out == "graph_title Connection Uptime\ngraph_args --base 1000 -l 0\ngraph_vlabel uptime in hours\ngraph_scale no\ngraph_category network\nuptime.label uptime\nuptime.draw AREA\ngraph_info The uptime in hours after the last disconnect.<br />Public IP address (ipv4): 127.0.0.1, Public IP address (ipv6): 0000::0000::0000::0000\n"

  def test_uptime(self, capsys):
    uptime = FritzboxConnectionUptime(get_fritzstatus_mock())
    uptime.print_stats()

    assert capsys.readouterr().out == "uptime.value 5.20\n"
