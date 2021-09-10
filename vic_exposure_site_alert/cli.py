"""Command-line interface for scheduling checks and alerts.

Run the check once unless a frequency (in minutes) is provided.
"""

import click

from .alert import main as alert
from .utils import start_logs

@click.group()
def main():
    """Run or schedule exposure site checks."""
    pass

@click.command()
def once():
    """Run a check now."""
    alert()

@click.command()
@click.option('--freq', type=click.IntRange(min=1), default=60, show_default=True, help="Frequency (in minutes) of scheduled checks.")
@click.option('--end', type=str, default="23:00", show_default=True, help="When scheduled checks will end.")
def every(freq, end):
    """Schedule checks in the future."""
    alert(freq, end)

main.add_command(once)
main.add_command(every)

if __name__ == '__main__':
    cli_logger = start_logs('cli', 7)
    cli_logger.debug('Called from command line')
    main()
