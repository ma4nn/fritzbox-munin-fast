#!/usr/bin/env python3
"""
  fritzbox_link_saturation - A munin plugin for Linux to monitor AVM Fritzbox
  WAN link saturation with QoS stats
  Copyright (C) 2019 Rene Walendy
  Author: Rene Walendy
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0

  Add the following section to your munin-node's plugin configuration:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_password [fritzbox password]
  env.fritzbox_user [fritzbox user, set any value if not required]

  This plugin supports the following munin configuration parameters:
  #%# family=auto contrib
  #%# capabilities=autoconf
"""

import sys
import json
from FritzboxInterface import FritzboxInterface

PAGE = 'data.lua'
PARAMS = {'xhr':1, 'lang':'de', 'page':'netMoni', 'xhrId':'updateGraphs', 'useajax':1, 'no_sidrenew':None}

DATA_UP   = ['us_realtime_bps_curr', 'us_important_bps_curr', 'us_default_bps_curr', 'us_background_bps_curr']
LABELS_UP = ['realtime', 'high', 'default', 'low']
DATA_DN   = ['ds_bps_curr', 'ds_mc_bps_curr']
LABELS_DN = ['internet', 'iptv']

def average_bps(datapoints):
  avg = 0
  for datapoint in datapoints:
    avg+=datapoint
  avg = avg//len(datapoints)
  return avg

def print_link_saturation():
  """get the current DSL link saturation"""

  jsondata = FritzboxInterface().post_age_with_login(PAGE, data=PARAMS)["data"]["sync_groups"][0]

  maxup = int(jsondata['upstream'])
  maxdown = int(jsondata['downstream'])

  print("multigraph saturation_up")
  for i, value in enumerate(DATA_UP):
    print('up_' + LABELS_UP[i] + '.value ' + str(average_bps(jsondata[value])))
  print("maxup.value " + str(maxup))
  print("multigraph saturation_down")
  for i, value in enumerate(DATA_DN):
    print('dn_' + LABELS_DN[i] + '.value ' + str(average_bps(jsondata[value])))
  print("maxdown.value " + str(maxdown))

def print_config():
  print("multigraph saturation_up")
  print("graph_title Uplink saturation")
  print("graph_vlabel bits out per ${graph_period}")
  print("graph_category network")
  print("graph_args --base 1000 --lower-limit 0")
  print("graph_order " + ' '.join(LABELS_UP) + " maxdown")
  for label in LABELS_UP:
    print('up_' + label + '.label ' + label)
    print('up_' + label + '.type GAUGE')
    print('up_' + label + '.draw AREASTACK')
    print('up_' + label + '.cdef up_' + label + ',8,*')
  print("maxup.label MAX")
  print("maxup.type GAUGE")
  print("maxup.graph LINE1")

  print("multigraph saturation_down")
  print("graph_title Downlink saturation")
  print("graph_vlabel bits in per ${graph_period}")
  print("graph_category network")
  print("graph_args --base 1000 --lower-limit 0")
  print("graph_order " + ' '.join(LABELS_DN) + " maxup")
  for label in LABELS_DN:
    print('dn_' + label + '.label ' + label)
    print('dn_' + label + '.type GAUGE')
    print('dn_' + label + '.draw AREASTACK')
    print('dn_' + label + '.cdef dn_' + label + ',8,*')
  print("maxdown.label MAX")
  print("maxdown.type GAUGE")
  print("maxdown.graph LINE1")

if __name__ == "__main__":
  if len(sys.argv) == 2 and sys.argv[1] == 'config':
    print_config()
  elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
    print("yes")  # Some docs say it'll be called with fetch, some say no arg at all
  elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'fetch'):
    try:
      print_link_saturation()
    except Exception as e:
      sys.exit("Couldn't retrieve fritzbox link saturation: " + str(e))
