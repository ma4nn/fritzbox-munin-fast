import os
import unittest
from base_test_case import BaseTestCase
import test.test_fritzbox_connection_uptime
import test.test_fritzbox_dsl
import test.test_fritzbox_ecostat
import test.test_fritzbox_energy
import test.test_fritzbox_traffic

def load_tests(loader, standard_tests, pattern):
    for fritzbox_model in ['7590-7.28']: # execute tests for each fritzbox model fixture
      standard_tests.addTest(loader.loadTestsFromTestCase(test.test_fritzbox_connection_uptime.TestFritzboxConnectionUptime))
      standard_tests.addTest(BaseTestCase.parametrize(test.test_fritzbox_dsl.TestFritzboxDsl, param=fritzbox_model))
      standard_tests.addTest(BaseTestCase.parametrize(test.test_fritzbox_ecostat.TestFritzboxEcostat, param=fritzbox_model))
      standard_tests.addTest(BaseTestCase.parametrize(test.test_fritzbox_energy.TestFritzboxEnergy, param=fritzbox_model))
      standard_tests.addTest(loader.loadTestsFromTestCase(test.test_fritzbox_traffic.TestFritzboxTraffic))

    return standard_tests