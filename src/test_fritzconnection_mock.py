import os
import json


class FritzConnectionMock: # pylint: disable=too-few-public-methods
  version: str

  def __init__(self, version):
    self.version = version

  def call_action(self, *args, **kwargs) -> {}:
    index = 0
    if 'arguments' in kwargs and 'NewIndex' in kwargs['arguments']:
      index = kwargs['arguments']['NewIndex']

    json_object = self.get_device_information_list()

    return json_object[index] if len(json_object) > index else {}

  def get_device_information_list(self, *args, **kwargs) -> {}:
    file_name = 'smart_home_devices.json'
    file_dir = f"{os.path.dirname(__file__)}/fixtures/fritzbox{self.version}"
    with open(file_dir + "/" + file_name, "r", encoding="utf-8") as file:
      return json.load(file)
