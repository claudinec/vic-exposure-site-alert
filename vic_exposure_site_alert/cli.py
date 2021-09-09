"""Command-line interface for scheduling checks and alerts.

Run the check once unless a frequency (in minutes) is provided.
"""

import click

import .vic_exposure_site_alert

@click.group()
def main():
    pass

@main.command()
def once():
    vic_exposure_site_alert()

@main.command()
@main.option('--freq', type=click.IntRange(min=1), default=60, show_default=True)
@main.option('--end', type=str, default="23:00", show_default=True)
def every(freq, end):
    vic_exposure_site_alert(freq, end)

if __name__ == '__main__':
    main()
