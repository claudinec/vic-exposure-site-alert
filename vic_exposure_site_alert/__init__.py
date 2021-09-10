"""Filtered Victorian Covid-19 exposure site alerts.

This package queries the Victorian Government Covid-19 exposure site
data for chosen suburbs and sends an alert for each new exposure site 
added via Pushcut for iOS.
"""

__version__ = '0.3.0'
__author__ = 'Claudine Chionh'

from .cli import main as cli
