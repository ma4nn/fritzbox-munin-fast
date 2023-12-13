#!/usr/bin/env python3
"""
  Unit tests for smart home temperature module
"""

import pytest
from unittest.mock import MagicMock
from fritzbox_smart_home_temperature import FritzboxSmartHomeTemperature


@pytest.mark.parametrize("connection", ["7590-7.57"], indirect=True)
class TestFritzboxSmartHome:
  def test_config(self, connection: MagicMock, capsys): # pylint: disable=unused-argument
    smart_home = FritzboxSmartHomeTemperature(connection)
    smart_home.print_config()

    assert capsys.readouterr().out == """graph_title Smart Home temperature
graph_vlabel degrees Celsius
graph_category sensors
graph_scale no
t16.label Lichterkette
t16.type GAUGE
t16.graph LINE
t16.info Temperature [FRITZ!DECT 210]
"""

  def test_smart_home(self, connection: MagicMock, capsys): # pylint: disable=unused-argument
    uptime = FritzboxSmartHomeTemperature(connection)
    uptime.print_stats()

    assert capsys.readouterr().out == "t16.value 7.0\n"
