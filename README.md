# Munin Plugins for FritzBox

A collection of munin plugins to monitor your AVM FRITZ!Box router. The scripts have been developed using a FRITZ!Box 7590 running FRITZ!OS 7.20.

If you are using the scripts on a different Fritz!Box model please let me know by

- opening an issue
- submitting a pull request

These python scripts are [Munin](http://munin-monitoring.org) plugins for monitoring the [Fritz!Box](https://avm.de/produkte/fritzbox/) router by AVM. They're build upon [fritzbox-munin](https://github.com/Tafkas/fritzbox-munin) with the goal to make use of the modern APIs that FritzOS 7 provides. No HTML Scraping is used. All data is fetched either through the TR-064 interface or the JSON API.

Contrary to the original version this fork uses multigraphs. This removes the need to query the same API endpoint multiple times. All multigraph plugins have configuration options to switch individual graphs on and off. 

## Requirements
- FritzBox router with Fritz!OS >= 07.20
- Munin 1.4.0 or later is required
- Python 3.x
   
## Available Plugins

### Connection Uptime
Plugin: `fritzbox_connection_uptime.py`  
Shows the WAN connection uptime.  
![Connection Uptime](doc/connection_uptime.png)

### DSL Errors
Plugin: `fritzbox_dsl.py`  
Multigraph plugin, showing:
 - DSL checksum errors
 - DSL transmission errors
 - line loss
 - link capacity
 - signal-to-noise ratio

### CPU & Memory
Plugin: `fritzbox_ecostat.py`  
Multigraph plugin, showing:
 - memory usage
 - CPU load
 - CPU temperature

### Smart Home Temperature
Plugin: `fritzbox_smart_home_temperature.py`  
![Smart Home Temperature](doc/smart_home_temperature.png)

### Energy
Plugin: `fritzbox_energy.py`  
Multigraph plugin, showing:
 - power consumption for CPU, WiFi, WAN, Fon, USB and total
 - devices connected on WiFi and LAN
 - system uptime

### Link Saturation
Plugin: `fritzbox_link_saturation.py`  
Multigraph plugin, showing saturation of WAN uplink and downlink by QoS priority

### Traffic
Plugin: `fritzbox_traffic.py`  
Similar to fritzbox_link_saturation, but single-graph and without QoS monitoring.

### WIFI
Plugin: `fritzbox_wifi_load.py`  
Multigraph plugin, showing for 2.4GHz and 5GHz
 - WiFi uplink and downlink bandwidth usage
 - neighbor APs on same and on different channels

## Installation & Configuration

1. Pre-requisites for the `fritzbox_traffic` and `fritzbox_connection_uptime` plugins are the [fritzconnection](https://pypi.python.org/pypi/fritzconnection) and [requests](https://pypi.python.org/pypi/requests) package. To install run

        pip install -r requirements.txt

1. Make sure the FritzBox has UPnP status information enabled. (web interface: _Home Network > Network > Network Settings > Universal Plug & Play (UPnP)_)

1. Copy all the scripts to `/usr/share/munin/plugins`

1. (optional) If you want to connect to FritzBox using SSL, download the Fritz certificate (web interface: _Internet > Freigaben > FritzBox Dienste > Zertifikat > Zertifikat herunterladen_) and save it to `/etc/munin/box.cer`.

1. Create entry in `/etc/munin/plugin-conf.d/munin-node`:

        [fritzbox_*]
        env.fritzbox_password <fritzbox_password>
        env.fritzbox_user <fritzbox_user>
        env.fritzbox_use_tls true
        host_name fritzbox
   
   See the plugin files for plugin-specific configuration options.

1. For each plugin you want to activate, create a symbolic link to `/etc/munin/plugins`.

1. Restart the munin-node daemon: `service munin-node restart`.

1. Done. You should now start to see the charts on the Munin pages!

## Localization

The `fritzbox_energy` script depends on the language selected in your fritzbox. Currently, two locales are
supported:

1. German: `de` (default)
2. English: `en`

You can change the used locale by setting an environment variable in your plugin configuration:

    env.locale en

## Different hosts for the FritzBox and your system

You can split the graphs of your FritzBox from the localhost graphs by following the next steps:

1. Use the following as your host configuration in `/etc/munin/munin.conf`

        [home.yourhost.net;server]
            address 127.0.0.1
            use_node_name yes


        [home.yourhost.net;fritzbox]
            address 127.0.0.1
            use_node_name no

1. Restart your munin-node: `service restart munin-node`

## Testing

To test a plugin use
```
munin-run --debug fritzbox_connection_uptime.py
```