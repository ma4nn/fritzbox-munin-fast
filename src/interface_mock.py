import json
import os
from unittest.mock import Mock

class FritzboxInterfaceMock(Mock):
  def __init__(self, version="7590-7.57"): # FritzOS version used
    super(Mock).__init__()
    self.version = version

  def get_page_with_login(self, page: str, data=None) -> str:
    return self.__side_effect_func_page_with_login(page, data)

  def post_page_with_login(self, page: str, data=None) -> dict:
    return self.__side_effect_func_page_with_login(page, data)

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
