import os
import re


_BASE_LANGUAGE_REGEX = re.compile(r"^(?P<base_language>[^+]+)\+[^+].*$")


def base_language(language: str) -> str:
    base_language_match = _BASE_LANGUAGE_REGEX.match(language)
    return (
        language
        if base_language_match is None
        else base_language_match.group("base_language")
    )


def extension_classifier(filename: str, pygments_class: str) -> str:
    return "." + os.path.basename(filename).split(".", 1)[-1]


def pygments_classifier(filename: str, pygments_class: str) -> str:
    return pygments_class
