"""
Pygount counts lines of source code using pygments lexers.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
from pygount.analysis import encoding_for, DuplicatePool, SourceAnalysis, SourceScanner, SourceState, source_analysis
from pygount.common import __version__, Error, OptionError

__all__ = [
    "encoding_for",
    "DuplicatePool",
    "Error",
    "OptionError",
    "SourceAnalysis",
    "SourceScanner",
    "SourceState",
    "source_analysis",
    "__version__",
]
