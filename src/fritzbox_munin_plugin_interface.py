import os
import sys


class MuninPluginInterface:
  def print_config(self) -> str:
    """Print the configuration for the Munin plugin."""
    pass

  def print_stats(self) -> dict:
    """Print the statistics for the Munin plugin."""
    pass


def main_handler(plugin: MuninPluginInterface):
  if len(sys.argv) == 2 and sys.argv[1] == 'config':
    plugin.print_config()
  elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
    print("yes")  # Some docs say it'll be called with fetch, some say no arg at all
  elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'fetch'):
    try:
      plugin.print_stats()
    except Exception as e:
      sys.exit(f"Couldn't retrieve Fritzbox stats of {os.path.basename(sys.argv[0])}/{type(plugin).__name__}: {str(e)}")
