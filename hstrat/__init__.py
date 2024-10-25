"""Top-level package for hstrat."""

__author__ = """Matthew Andres Moreno"""
__email__ = "m.more500@gmail.com"
__version__ = "1.12.0"

from lazy_loader import attach_stub

__getattr__, __dir__, __all__ = attach_stub(__name__, __file__)
