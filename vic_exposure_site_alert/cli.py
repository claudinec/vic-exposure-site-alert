"""Command-line interface for scheduling checks and alerts.

Run the check once unless a frequency (in minutes) is provided.
"""

import click

from .alert import main as alert

@click.group()
def main():
    pass

@click.command()
def once():
    alert()

@click.command()
@click.option('--freq', type=click.IntRange(min=1), default=60, show_default=True)
@click.option('--end', type=str, default="23:00", show_default=True)
def every(freq, end):
    alert(freq, end)

main.add_command(once)
main.add_command(every)

if __name__ == '__main__':
    main()
