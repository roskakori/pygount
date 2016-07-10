"""
Pygount counts lines of source code using pygments lexers.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
from pygount.analysis import encoding_for, SourceAnalysis, source_analysis

__all__ = [
    'encoding_for',
    'SourceAnalysis',
    'source_analysis',
    '__version__',
]

__version__ = '0.2'
