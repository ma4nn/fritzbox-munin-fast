"""
    From https://eli.thegreenplace.net/2011/08/02/python-unit-testing-parametrized-test-cases/
"""

import json
import unittest
from unittest.mock import Mock

class BaseTestCase(unittest.TestCase):
  """ TestCase classes that want to be parametrized should
      inherit from this class.
  """
  def __init__(self, methodName='runTest', param=None):
    super(BaseTestCase, self).__init__(methodName)
    self.param = param

  @staticmethod
  def parametrize(testcase_klass, param=None):
    """ Create a suite containing all tests taken from the given
        subclass, passing them the parameter 'param'.
    """
    testloader = unittest.TestLoader()
    testnames = testloader.getTestCaseNames(testcase_klass)
    suite = unittest.TestSuite()
    for name in testnames:
      suite.addTest(testcase_klass(name, param=param))
    return suite

  def __side_effect_func_page_with_login(self, page: str, data):
    if (page == 'internet/inetstat_monitor.lua'):
      file = open(f"tests/fritzbox{self.param}/inetstat_monitor_lua.txt", "r")
      return file.read()
    elif (page == 'internet/dsl_stats_tab.lua'):
      file = open(f"tests/fritzbox{self.param}/dsl_stats_tab_lua.txt", "r")
      return file.read()
    elif (page == 'data.lua'):
      file = open(f"tests/fritzbox{self.param}/data_lua.txt", "r")
      return json.loads(file.read())

    return ''

  def _get_interface_mock(self) -> Mock:
    mock_interface = Mock()
    mock_interface.get_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)
    mock_interface.post_page_with_login = Mock(side_effect=self.__side_effect_func_page_with_login)

    return mock_interface