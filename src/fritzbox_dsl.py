#!/usr/bin/env python3
"""
  fritzbox_dsl - A munin plugin for Linux to monitor AVM Fritzbox DSL link quality
  stats
  Copyright (C) 2019 Rene Walendy
  Author: Rene Walendy
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0

  Add the following section to your munin-node's plugin configuration:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_password [fritzbox password]
  env.fritzbox_user [fritzbox user, set any value if not required]
  env.dsl_modes [capacity] [snr] [damping] [errors] [crc]

  This plugin supports the following munin configuration parameters:
  #%# family=auto contrib
  #%# capabilities=autoconf
"""

import os
import sys
from FritzboxInterface import FritzboxInterface

PAGE = 'data.lua'
PARAMS = {'xhr':1, 'lang':'de', 'page':'dslStat', 'xhrId':'refresh', 'useajax':1, 'no_sidrenew':None}

TITLES = {
  'capacity': 'Link Capacity',
  'rate': 'Synced Rate',
  'snr': 'Signal-to-Noise Ratio',
  'damping': 'Line Loss',
  'errors': 'Transmission Errors',
  'crc': 'Checksum Errors',
  'ecc': 'Error Correction'
}
TYPES = {
  'capacity': 'GAUGE',
  'rate': 'GAUGE',
  'snr': 'GAUGE',
  'damping': 'GAUGE',
  'errors': 'DERIVE',
  'crc': 'GAUGE',
  'ecc': 'GAUGE'
}
VLABELS = {
  'capacity': 'bit/s',
  'rate': 'bit/s',
  'snr': 'dB',
  'damping': 'dB',
  'errors': 's',
  'crc': 'n',
  'ecc': 'n',
}

def get_modes():
  return os.getenv('dsl_modes').split(' ') if (os.getenv('dsl_modes')) else []

def print_graph(name, recv, send, prefix=""):
  if name:
    print("multigraph " + name)
  print(prefix + "recv.value " + recv)
  print(prefix + "send.value " + send)

class FritzboxDsl:
  __connection = None

  def __init__(self, fritzbox_interface: FritzboxInterface = None):
    self.__connection = fritzbox_interface if (fritzbox_interface) else FritzboxInterface()

  def print_dsl_stats(self):
    """print the current DSL statistics"""

    modes = get_modes()
    jsondata = self.__connection.post_page_with_login(PAGE, data=PARAMS)['data']

    # us=upstream, ds=downstream

    if 'capacity' in modes:
      print_graph("dsl_capacity", jsondata['negotiatedValues'][2]['val'][0]['ds'], jsondata['negotiatedValues'][2]['val'][0]['us'])

    if 'rate' in modes:
      print_graph("dsl_rate", jsondata['negotiatedValues'][3]['val'][0]['ds'], jsondata['negotiatedValues'][3]['val'][0]['us'])

    if 'snr' in modes: # Störabstandsmarge
      print_graph("dsl_snr", jsondata['negotiatedValues'][12]['val'][0]['ds'], jsondata['negotiatedValues'][12]['val'][0]['us'])

    if 'damping' in modes: # Leitungsdämpfung
      print_graph("dsl_damping", jsondata['negotiatedValues'][13]['val'][0]['ds'], jsondata['negotiatedValues'][13]['val'][0]['us'])

    if 'errors' in modes:
      print_graph("dsl_errors", jsondata['errorCounters'][1]['val'][0]['ds'], jsondata['errorCounters'][1]['val'][0]['us'], prefix="es_")
      print_graph(None, jsondata['errorCounters'][2]['val'][0]['ds'], jsondata['errorCounters'][2]['val'][0]['us'], prefix="ses_")

    if 'crc' in modes:
      print_graph("dsl_crc", jsondata['errorCounters'][5]['val'][0]['ds'], jsondata['errorCounters'][1]['val'][0]['us'])

    if 'ecc' in modes:
      print_graph("dsl_ecc", jsondata['errorCounters'][9]['val'][0]['ds'], jsondata['errorCounters'][9]['val'][0]['us'], prefix="corr_")
      print_graph(None, jsondata['errorCounters'][13]['val'][0]['ds'], jsondata['errorCounters'][13]['val'][0]['us'], prefix="fail_")

  def retrieve_max_values(self):
    max_values = {'send': 0, 'recv': 0}
    jsondata = self.__connection.post_page_with_login(PAGE, data=PARAMS)['data']

    if not 'negotiatedValues' in jsondata:
      return max_values

    # retrieve values from "Leitungskapazitaet"
    max_values['send'] = int(float(jsondata['negotiatedValues'][2]['val'][0]['us']))
    max_values['recv'] = int(float(jsondata['negotiatedValues'][2]['val'][0]['ds']))

    return max_values

  def print_config(self):
    modes = get_modes()
    max_values = self.retrieve_max_values()

    for mode in ['capacity', 'rate', 'snr', 'damping', 'crc']:
      if not mode in modes:
        continue
      print("multigraph dsl_" + mode)
      print("graph_title " + TITLES[mode])
      print("graph_vlabel " + VLABELS[mode])
      print("graph_args --lower-limit 0")
      print("graph_category network")
      for p, l in {'recv': 'receive', 'send': 'send'}.items():
        print(p + ".label " + l)
        print(p + ".type " + TYPES[mode])
        print(p + ".graph LINE1")
        print(p + ".min 0")
        if mode in ['capacity', 'rate']:
          print(p + ".cdef " + p + ",1000,*")
          print(p + ".warning " + str(max_values[p]))

    if 'errors' in modes:
      print("multigraph dsl_errors")
      print("graph_title " + TITLES['errors'])
      print("graph_vlabel " + VLABELS['errors'])
      print("graph_args --lower-limit 0")
      print("graph_category network")
      print("graph_order es_recv es_send ses_recv ses_send")
      for p, l in {'es_recv': 'receive errored', 'es_send': 'send errored', 'ses_recv': 'receive severely errored', 'ses_send': 'send severely errored'}.items():
        print(p + ".label " + l)
        print(p + ".type " + TYPES['errors'])
        print(p + ".graph LINE1")
        print(p + ".min 0")
        print(p + ".warning 1")

    if 'ecc' in modes:
      print("multigraph dsl_ecc")
      print("graph_title " + TITLES['ecc'])
      print("graph_vlabel " + VLABELS['ecc'])
      print("graph_args --lower-limit 0")
      print("graph_category network")
      print("graph_order corr_recv corr_send fail_recv fail_send")
      for p, l in {'corr_recv' : 'receive corrected', 'corr_send': 'send corrected', 'fail_recv' : 'receive uncorrectable', 'fail_send': 'send uncorrectable'}.items():
        print(p + ".label " + l)
        print(p + ".type " + TYPES['ecc'])
        print(p + ".graph LINE1")
        print(p + ".min 0")
        print(p + ".warning 1")


if __name__ == "__main__":
  dsl = FritzboxDsl()

  if len(sys.argv) == 2 and sys.argv[1] == 'config':
    dsl.print_config()
  elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
    print("yes")  # Some docs say it'll be called with fetch, some say no arg at all
  elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'fetch'):
    try:
      dsl.print_dsl_stats()
    except Exception as e:
      sys.exit("Couldn't retrieve fritzbox dsl stats: " + str(e))
