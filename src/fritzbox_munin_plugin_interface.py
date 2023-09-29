class MuninPluginInterface:
  def print_config(self) -> str:
    """Print the configuration for the Munin plugin."""
    pass

  def print_stats(self) -> dict:
    """Print the statistics for the Munin plugin."""
    pass
