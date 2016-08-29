"""
Common classes and functions for pygount.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
__version__ = '0.3'


class Error(Exception):
    pass


class OptionError(Error):
    def __init__(self, message, source=None):
        super().__init__(message)
        self.option_error_message = (source + ': ') if source is not None else ''
        self.option_error_message += message

    def __str__(self):
        return self.option_error_message
