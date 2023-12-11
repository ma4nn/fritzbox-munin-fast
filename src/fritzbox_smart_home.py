#!/usr/bin/env python3
"""
  fritzbox_smart_home_temperature - A munin plugin for Linux to monitor AVM Fritzbox SmartHome temperatures

  @see https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_homeauto.pdf
"""

import sys
from fritzconnection import FritzConnection
from fritzbox_config import FritzboxConfig
from fritzbox_munin_plugin_interface import MuninPluginInterface,main_handler


class FritzboxSmartHome(MuninPluginInterface):
  def print_stats(self):
    smartHomeData = self.__retrieve_smart_home()
    """get the current cpu temperature"""

    print("multigraph temperatures")
    for data in smartHomeData:
      if (data['NewTemperatureIsValid'] == 'VALID'):
        print (f"t{data['NewDeviceId']}.value {float(data['NewTemperatureCelsius']) / 10}")
    print("multigraph energy")
    for data in smartHomeData:
      if (data['NewMultimeterIsValid'] == 'VALID'):
        print (f"e{data['NewDeviceId']}.value {data['NewMultimeterEnergy']}")
    print("multigraph powers")
    for data in smartHomeData:
      if (data['NewMultimeterIsValid'] == 'VALID'):
        print (f"p{data['NewDeviceId']}.value {float(data['NewMultimeterPower']) / 100}")
    print("multigraph states")
    for data in smartHomeData:
      if (data['NewSwitchIsValid'] == 'VALID'):
        state = 1
        if data['NewSwitchState'] == 'OFF':
          state = 0
        print (f"s{data['NewDeviceId']}.value {state}")

  def print_config(self):
    smartHomeData = self.__retrieve_smart_home()
    print("multigraph temperatures")
    print("graph_title Smart Home temperature")
    print("graph_vlabel degrees Celsius")
    print("graph_category sensors")
    print("graph_scale no")

    for data in smartHomeData:
      if (data['NewTemperatureIsValid'] == 'VALID'):
        print (f"t{data['NewDeviceId']}.label {data['NewDeviceName']}")
        print (f"t{data['NewDeviceId']}.type GAUGE")
        print (f"t{data['NewDeviceId']}.graph LINE")
        print (f"t{data['NewDeviceId']}.info Temperature [{data['NewProductName']}] Offset: {float(data['NewTemperatureOffset']) / 10}°C")

    print("multigraph energy")
    print("graph_title Smart Home energy consumption")
    print("graph_vlabel Wh")
    print("graph_category sensors")
    print("graph_scale no")
    print("graph_period hour")
    for data in smartHomeData:
      if (data['NewMultimeterIsValid'] == 'VALID'):
        print (f"e{data['NewDeviceId']}.label {data['NewDeviceName']}")
        print (f"e{data['NewDeviceId']}.type DERIVE")
        print (f"e{data['NewDeviceId']}.graph LINE")
        print (f"e{data['NewDeviceId']}.info Energy consumption (Wh) [{data['NewProductName']}]")

    print("multigraph powers")
    print("graph_title Smart Home powers")
    print("graph_vlabel W")
    print("graph_category sensors")
    print("graph_scale no")
    for data in smartHomeData:
      if (data['NewMultimeterIsValid'] == 'VALID'):
        print (f"p{data['NewDeviceId']}.label {data['NewDeviceName']}")
        print (f"p{data['NewDeviceId']}.type GAUGE")
        print (f"p{data['NewDeviceId']}.graph LINE")
        print (f"p{data['NewDeviceId']}.info Power (W) [{data['NewProductName']}]")

    print("multigraph states")
    print("graph_title Smart Home switch states")
    print("graph_vlabel State")
    print("graph_category sensors")
    print("graph_scale no")
    for data in smartHomeData:
      if (data['NewSwitchIsValid'] == 'VALID'):
        print (f"s{data['NewDeviceId']}.label {data['NewDeviceName']}")
        print (f"s{data['NewDeviceId']}.type GAUGE")
        print (f"s{data['NewDeviceId']}.graph LINE")
        print (f"s{data['NewDeviceId']}.info Switch state [{data['NewProductName']}]")

  def __retrieve_smart_home(self):
    smart_home_data = []
    config = FritzboxConfig()

    try:
      connection = FritzConnection(address=config.server, user=config.user, password=config.password, use_tls=config.use_tls)
    except Exception as e:
      sys.exit("Couldn't get data: " + str(e))

    for i in range(0, 20):
      try:
        data = connection.call_action('X_AVM-DE_Homeauto1', 'GetGenericDeviceInfos', arguments={'NewIndex': i})
        smart_home_data.append(data)
      except Exception as e:
        # smart home device index does not exist, so we stop here
        break

    return smart_home_data


if __name__ == '__main__':
  main_handler(FritzboxSmartHome())
