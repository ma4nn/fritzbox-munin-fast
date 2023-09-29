#!/usr/bin/env python3
"""
  fritzbox_smart_home_temperature - A munin plugin for Linux to monitor AVM Fritzbox SmartHome temperatures

  @see https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_homeauto.pdf
"""

import sys
from fritzconnection import FritzConnection
from fritzbox_config import FritzboxConfig
from fritzbox_munin_plugin_interface import MuninPluginInterface,main_handler


class FritzboxSmartHomeTemperature(MuninPluginInterface):
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
    config = FritzboxConfig()

    try:
      connection = FritzConnection(address=config.server, user=config.user, password=config.password, use_tls=config.use_tls)
    except Exception as e:
      sys.exit("Couldn't get temperature: " + str(e))

    for i in range(0, 20):
      try:
        data = connection.call_action('X_AVM-DE_Homeauto1', 'GetGenericDeviceInfos', arguments={'NewIndex': i})
        if (data['NewTemperatureIsEnabled']):
          smart_home_data.append(data)
      except Exception as e:
        # smart home device index does not exist, so we stop here
        break

    return smart_home_data


if __name__ == '__main__':
  main_handler(FritzboxSmartHomeTemperature())
