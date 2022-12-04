"""
Common classes and functions for pygount.
"""
# Copyright (c) 2016-2022, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import contextlib
import fnmatch
import functools
import inspect
import re
import warnings
from typing import Generator, List, Optional, Pattern, Sequence, Union

#: Pseudo pattern to indicate that the remaining pattern are an addition to the default patterns.

ADDITIONAL_PATTERN = "[...]"

#: Prefix to use for pattern strings to describe a regular expression instead of a shell pattern.
REGEX_PATTERN_PREFIX = "[regex]"

_REGEX_TYPE = type(re.compile(""))


class Error(Exception):
    """
    Error to indicate that something went wrong during a pygount run.
    """

    pass


class OptionError(Error):
    """
    Error to indicate that a value passed to a command line option must be
    fixed.
    """

    def __init__(self, message, source=None):
        super().__init__(message)
        self.option_error_message = (source + ": ") if source is not None else ""
        self.option_error_message += message

    def __str__(self):
        return self.option_error_message


def as_list(items_or_text: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(items_or_text, str):
        # TODO: Allow to specify comma (,) in text using '[,]'.
        result = [item.strip() for item in items_or_text.split(",") if item.strip() != ""]
    else:
        result = list(items_or_text)
    return result


def regex_from(pattern: Union[str, Pattern], is_shell_pattern=False) -> Pattern:
    assert pattern is not None
    if isinstance(pattern, str):
        if is_shell_pattern:
            result = re.compile(fnmatch.translate(pattern))
        else:
            result = re.compile(pattern)
    else:
        result = pattern  # Assume pattern already is a compiled regular expression
    return result


def regexes_from(
    patterns_text: Union[str, Sequence[str]],
    default_patterns_text: Optional[Union[str, Sequence[str]]] = None,
    source: Optional[str] = None,
) -> List[Pattern]:
    assert patterns_text is not None

    result = []
    default_regexes = []
    try:
        if isinstance(patterns_text, str):
            is_shell_pattern = True
            patterns_text_without_prefixes = patterns_text
            if patterns_text_without_prefixes.startswith(REGEX_PATTERN_PREFIX):
                is_shell_pattern = False
                patterns_text_without_prefixes = patterns_text_without_prefixes[len(REGEX_PATTERN_PREFIX) :]
            if patterns_text_without_prefixes.startswith(ADDITIONAL_PATTERN):
                assert default_patterns_text is not None
                default_regexes = regexes_from(default_patterns_text)
                patterns_text_without_prefixes = patterns_text_without_prefixes[len(ADDITIONAL_PATTERN) :]

            patterns = as_list(patterns_text_without_prefixes)
            for pattern in patterns:
                result.append(regex_from(pattern, is_shell_pattern))
        else:
            regexes = list(patterns_text)
            if len(regexes) >= 1 and regexes[0] is None:
                default_regexes = regexes_from(default_patterns_text)
                regexes = regexes[1:]
            for supposed_regex in regexes:
                assert isinstance(supposed_regex, _REGEX_TYPE), (
                    "patterns_text must a text or sequnce or regular expressions but contains: %a" % supposed_regex
                )
            result.extend(regexes)
    except re.error as error:
        raise OptionError(f"cannot parse pattern for regular repression: {error}", source)
    result.extend(default_regexes)
    return result


def lines(text: str) -> Generator[str, None, None]:
    """
    Generator function to yield lines (delimited with ``'\n'``) stored in
    ``text``. This is useful when a regular expression should only match on a
    per line basis in a memory efficient way.
    """
    assert text is not None
    assert "\r" not in text
    previous_newline_index = 0
    newline_index = text.find("\n")
    while newline_index != -1:
        yield text[previous_newline_index:newline_index]
        previous_newline_index = newline_index + 1
        newline_index = text.find("\n", previous_newline_index)
    last_line = text[previous_newline_index:]
    if last_line != "":
        yield last_line


def deprecated(reason: Optional[str]):  # pragma: no cover
    """
    Decorator to mark functions as deprecated and log a warning in case it is called.

    Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
    """

    if isinstance(reason, str):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):
            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason), category=DeprecationWarning, stacklevel=2
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator
    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(fmt2.format(name=func2.__name__), category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2
    else:
        raise TypeError(repr(type(reason)))


nullcontext = contextlib.nullcontext
