import io
import json
import os
import unittest
from unittest.mock import Mock
from typing import Callable


# pylint: disable=too-few-public-methods
class BaseTestCase():
  version: str

  @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
  def assert_stdout(self, expected_output, method: Callable[[], str], mock_stdout):
    method()
    output = mock_stdout.getvalue()
    assert expected_output == output.rstrip("\n")

  def __side_effect_func_page_with_login(self, page: str, data) -> dict | str:
    file_dir = f"{os.path.dirname(__file__)}/fixtures/fritzbox{self.version}"

    if page == 'internet/dsl_stats_tab.lua':
      with open(file_dir + "/dsl_stats_tab_lua.html", "r", encoding="utf-8") as file:
        return file.read()

    file_name = None
    if page == 'internet/inetstat_monitor.lua':
      file_name = "inetstat_monitor_lua.json"
    elif page == 'data.lua' and data['page'] == 'ecoStat':
      file_name = "ecostat_data_lua.json"
    elif page == 'data.lua' and data['page'] == 'energy':
      file_name = "energy_data_lua.json"
    elif page == 'data.lua' and data['page'] == 'dslStat':
      file_name = "dsl_data_lua.json"

    if file_name is not None:
      with open(file_dir + "/" + file_name, "r", encoding="utf-8") as file:
        return json.load(file)

    if page == 'data.lua':
      return {"data": {}}

    return ''

  def _create_interface_mock(self, fixture_version="7590-7.57") -> Mock:
    self.version = fixture_version

    mock_interface = Mock()
    mock_interface.get_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)
    mock_interface.post_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)

    return mock_interface
