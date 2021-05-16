"""
Pygount counts lines of source code using pygments lexers.
"""
# Copyright (c) 2016-2021, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
from .analysis import DuplicatePool, SourceAnalysis, SourceScanner, SourceState, encoding_for, source_analysis
from .common import Error, OptionError, __version__
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
