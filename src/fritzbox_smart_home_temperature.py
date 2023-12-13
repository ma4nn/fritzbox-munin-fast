#!/usr/bin/env python3
"""
  fritzbox_smart_home_temperature - A munin plugin for Linux to monitor AVM Fritzbox SmartHome temperatures

  @see https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_homeauto.pdf
"""

from fritzconnection import FritzConnection
from fritzbox_config import FritzboxConfig
from fritzbox_munin_plugin_interface import MuninPluginInterface,main_handler


class FritzboxSmartHomeTemperature(MuninPluginInterface):
  __connection = None

  def __init__(self, fritzbox_connection: FritzConnection):
    self.__connection = fritzbox_connection

  def print_stats(self):
    """get the current cpu temperature"""

    for data in self.__retrieve_smart_home_temps():
      print (f"t{data['NewDeviceId']}.value {float(data['NewTemperatureCelsius']) / 10}")

  def print_config(self):
    print("graph_title Smart Home temperature")
    print("graph_vlabel degrees Celsius")
    print("graph_category sensors")
    print("graph_scale no")

    for data in self.__retrieve_smart_home_temps():
      print (f"t{data['NewDeviceId']}.label {data['NewDeviceName']}")
      print (f"t{data['NewDeviceId']}.type GAUGE")
      print (f"t{data['NewDeviceId']}.graph LINE")
      print (f"t{data['NewDeviceId']}.info Temperature [{data['NewProductName']}]")

  def __retrieve_smart_home_temps(self):
    smart_home_data = []

    for i in range(0, 20):
      data = self.__connection.call_action('X_AVM-DE_Homeauto1', 'GetGenericDeviceInfos', arguments={'NewIndex': i})
      if 'NewTemperatureIsEnabled' in data and data['NewTemperatureIsEnabled']:
        smart_home_data.append(data)

    return smart_home_data


if __name__ == '__main__':
  config = FritzboxConfig()
  main_handler(FritzboxSmartHomeTemperature(FritzConnection(address=config.server, user=config.user, password=config.password, use_tls=config.use_tls)))
