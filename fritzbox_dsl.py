#!/usr/bin/env python
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
import json
import lxml.html as html
import fritzbox_helper as fh

PAGE = 'internet/dsl_stats_tab.lua'
PARAMS = {'update':'mainDiv', 'useajax':1, 'xhr':1}

TITLES = {
  'capacity': 'Link Capacity',
  'snr': 'Signal-to-Noise Ratio',
  'damping': 'Line Loss',
  'errors': 'Transmission Errors',
  'crc': 'Checksum Errors'
}
TYPES = {
  'capacity': 'GAUGE',
  'snr': 'GAUGE',
  'damping': 'GAUGE',
  'errors': 'DERIVE',
  'crc': 'GAUGE'
}
VLABELS = {
  'capacity': 'bit/s',
  'snr': 'dB',
  'damping': 'dB',
  'errors': 's',
  'crc': 'n'
}

def get_modes():
  return os.environ['dsl_modes'].split(' ')

def print_graph(name, recv, send, prefix=""):
  if name:
    print("multigraph " + name)
  print(prefix + "recv.value " + recv)
  print(prefix + "send.value " + send)

def print_energy_stats():
    """print the current DSL statistics"""
    
    modes = get_modes()

    server = os.environ['fritzbox_ip']
    password = os.environ['fritzbox_password']
    user = os.environ['fritzbox_user']
    
    # download the table
    data = fh.get_page_with_login(server, user, password, PAGE, params=PARAMS)
    root = html.fragments_fromstring(data)
    
    if 'capacity' in modes:
      capacity_recv = root[1].xpath('tr[position() = 4]/td[position() = 3]')[0].text
      capacity_send = root[1].xpath('tr[position() = 4]/td[position() = 4]')[0].text
      print_graph("dsl_capacity", capacity_recv, capacity_send)

    if 'snr' in modes:
      snr_recv = root[1].xpath('tr[position() = 12]/td[position() = 3]')[0].text
      snr_send = root[1].xpath('tr[position() = 12]/td[position() = 4]')[0].text
      print_graph("dsl_snr", snr_recv, snr_send)

    if 'damping' in modes:    
      damping_recv = root[1].xpath('tr[position() = 14]/td[position() = 3]')[0].text
      damping_send = root[1].xpath('tr[position() = 14]/td[position() = 4]')[0].text
      print_graph("dsl_damping", damping_recv, damping_send)

    if 'errors' in modes:    
      es_recv = root[4].xpath('tr[position() = 3]/td[position() = 2]')[0].text
      es_send = root[4].xpath('tr[position() = 4]/td[position() = 2]')[0].text
      ses_recv = root[4].xpath('tr[position() = 3]/td[position() = 3]')[0].text
      ses_send = root[4].xpath('tr[position() = 4]/td[position() = 3]')[0].text
      print_graph("dsl_errors", es_recv, es_send, prefix="es_")
      print_graph(None, ses_recv, ses_send, prefix="ses_")

    if 'crc' in modes:    
      crc_recv = root[4].xpath('tr[position() = 3]/td[position() = 4]')[0].text
      crc_send = root[4].xpath('tr[position() = 4]/td[position() = 4]')[0].text
      print_graph("dsl_crc", crc_recv, crc_send)

def print_config():
    modes = get_modes()

    for mode in ['capacity', 'snr', 'damping', 'crc']:
      if not mode in modes:
        continue
      print("multigraph dsl_" + mode)
      print("graph_title AVM Fritz!Box DSL " + TITLES[mode])
      print("graph_vlabel " + VLABELS[mode])
      print("graph_args --lower-limit 0")
      print("graph_category network")
      for p,l in {'recv' : 'receive', 'send': 'send'}.items():
        print(p + ".label " + l)
        print(p + ".type " + TYPES[mode])
        print(p + ".graph LINE1")
        print(p + ".min 0")
        if mode == 'capacity':
          print(p + ".cdef " + p + ",1000,*")

    if 'errors' in modes:
      print("multigraph dsl_errors")
      print("graph_title AVM Fritz!Box DSL " + TITLES['errors'])
      print("graph_vlabel " + VLABELS['errors'])
      print("graph_args --lower-limit 0")
      print("graph_category network")
      print("graph_order es_recv es_send ses_recv ses_send")
      for p,l in {'es_recv' : 'receive errored', 'es_send': 'send errored', 'ses_recv' : 'receive severely errored', 'ses_send': 'send severely errored'}.items():
        print(p + ".label " + l)
        print(p + ".type " + TYPES['errors'])
        print(p + ".graph LINE1")
        print(p + ".min 0")

    if os.environ.get('host_name'):
        print("host_name " + os.environ['host_name'])


if __name__ == "__main__":
  if len(sys.argv) == 2 and sys.argv[1] == 'config':
    print_config()
  elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
    print("yes")  # Some docs say it'll be called with fetch, some say no arg at all
  elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'fetch'):
#    try:
      print_energy_stats()
#    except:
#      sys.exit("Couldn't retrieve fritzbox energy stats")
