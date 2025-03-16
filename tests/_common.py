"""
Common constants and functions used by multiple tests.
"""

# Copyright (c) 2016-2024, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import os
import shutil
import unittest
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import IO, TextIO, Union

PYGOUNT_PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))
PYGOUNT_SOURCE_FOLDER = os.path.join(PYGOUNT_PROJECT_FOLDER, "pygount")


class TempFolderTest(unittest.TestCase):
    def setUp(self):
        self.tests_temp_folder = os.path.join(PYGOUNT_PROJECT_FOLDER, "tests", ".temp")
        os.makedirs(self.tests_temp_folder, exist_ok=True)

    def create_temp_file(
        self, relative_target_path, content: Union[str, bytes, Sequence[str]], encoding="utf-8", do_create_folder=False
    ):
        result = os.path.join(self.tests_temp_folder, relative_target_path)
        if do_create_folder:
            os.makedirs(os.path.dirname(result), exist_ok=True)
        with open(result, "w", encoding=encoding) as target_file:
            if isinstance(content, (str, bytes)):
                target_file.write(content)
            else:
                for line in content:
                    target_file.write(line)
                    target_file.write("\n")
        return result

    def create_temp_binary_file(self, relative_target_path, content: bytes):
        result = os.path.join(self.tests_temp_folder, relative_target_path)
        with open(result, "wb") as target_file:
            target_file.write(content)
        return result

    def tearDown(self):
        shutil.rmtree(self.tests_temp_folder)


@contextmanager
def temp_binary_file(data: bytes) -> Iterator[IO]:
    with NamedTemporaryFile(mode="wb+", suffix=".bin") as result:
        result.write(data)
        result.flush()
        result.seek(0)
        yield result


@contextmanager
def temp_source_file(suffix: str, lines: list[str], *, encoding: str = "utf-8") -> Iterator[TextIO]:
    with NamedTemporaryFile(encoding=encoding, mode="w+", suffix=f".{suffix}") as result:
        result.write("\n".join(lines))
        result.flush()
        result.seek(0)
        yield result
