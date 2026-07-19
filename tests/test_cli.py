from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from newcodespeak import __version__
from newcodespeak.cli import (
    EXIT_CENSORSHIP_ERROR,
    EXIT_IO_ERROR,
    EXIT_SUCCESS,
    main,
    read_source,
)


class CliTests(unittest.TestCase):
    def test_version_prints_package_version(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue(), f"ncs {__version__}\n")

    def test_missing_source_prints_help_and_returns_io_error(self) -> None:
        error_output = StringIO()

        with redirect_stderr(error_output):
            result = main([])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("usage: ncs", error_output.getvalue())

    def test_approved_source_is_loaded_without_execution(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "program.ncs"
            source_path.write_text(
                "approve quota;\nset quota to 1;\n", encoding="utf-8"
            )
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_SUCCESS)
        self.assertIn("loaded 31 character(s)", output.getvalue())
        self.assertIn("vocabulary passed", output.getvalue())
        self.assertIn("execution is not implemented yet", output.getvalue())

    def test_empty_source_is_a_censorship_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "empty.ncs"
            source_path.write_text("", encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_CENSORSHIP_ERROR)
        self.assertIn("must begin with an approve declaration", error_output.getvalue())

    def test_unapproved_source_word_returns_censorship_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "censored.ncs"
            source_path.write_text("approve quota; set memory to 1;", encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_CENSORSHIP_ERROR)
        self.assertIn("memory", error_output.getvalue())

    def test_missing_file_returns_io_error(self) -> None:
        error_output = StringIO()

        with redirect_stderr(error_output):
            result = main(["missing-file.ncs"])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("source file does not exist", error_output.getvalue())

    def test_non_utf8_file_returns_io_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "invalid.ncs"
            source_path.write_bytes(b"\xff")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("not valid UTF-8", error_output.getvalue())

    def test_read_source_rejects_a_directory(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OSError, "source path is a directory"):
                read_source(Path(directory))


if __name__ == "__main__":
    unittest.main()
