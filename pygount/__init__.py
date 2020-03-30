"""
Pygount counts lines of source code using pygments lexers.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
from .analysis import encoding_for, DuplicatePool, SourceAnalysis, SourceScanner, SourceState, source_analysis
from .common import __version__, Error, OptionError
from .summary import LanguageSummary, ProjectSummary

__all__ = [
    "encoding_for",
    "DuplicatePool",
    "Error",
    "LanguageSummary",
    "OptionError",
    "ProjectSummary",
    "SourceAnalysis",
    "SourceScanner",
    "SourceState",
    "source_analysis",
    "__version__",
]
