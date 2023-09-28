import io
import json
import os
import unittest
from unittest.mock import Mock
from typing import Callable

class BaseTestCase():
  version: str

  @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
  def assert_stdout(self, expected_output, method: Callable[[], str], mock_stdout):
    method()
    output = mock_stdout.getvalue()
    assert expected_output == output.rstrip("\n")

  def __side_effect_func_page_with_login(self, page: str, data) -> dict | str:
    current_dir = os.path.dirname(__file__)

    if page == 'internet/inetstat_monitor.lua':
      file = open(f"{current_dir}/fixtures/fritzbox{self.version}/inetstat_monitor_lua.json", "r")
      return json.load(file)
    elif page == 'internet/dsl_stats_tab.lua':
      file = open(f"{current_dir}/fixtures/fritzbox{self.version}/dsl_stats_tab_lua.html", "r")
      return file.read()
    elif page == 'data.lua' and data['page'] == 'ecoStat':
      file = open(f"{current_dir}/fixtures/fritzbox{self.version}/ecostat_data_lua.json", "r")
      return json.load(file)
    elif page == 'data.lua' and data['page'] == 'energy':
      file = open(f"{current_dir}/fixtures/fritzbox{self.version}/energy_data_lua.json", "r")
      return json.load(file)
    elif page == 'data.lua' and data['page'] == 'dslStat':
      file = open(f"{current_dir}/fixtures/fritzbox{self.version}/dsl_data_lua.json", "r")
      return json.load(file)
    elif page == 'data.lua':
      return {"data": {}}

    return ''

  def _create_interface_mock(self, fixture_version="7590-7.57") -> Mock:
    self.version = fixture_version

    mock_interface = Mock()
    mock_interface.get_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)
    mock_interface.post_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)

    return mock_interface