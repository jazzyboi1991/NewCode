import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from newcode.cli import format_source, main


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(list(args))
        return code, output.getvalue(), errors.getvalue()

    def test_check_trace_reports_all_validation_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.2\nspeak 1\n", encoding="utf-8")
            code, output, errors = self.run_cli("check", str(path), "--trace")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("[LEX] approved", output)
        self.assertIn("[PARSE] approved", output)
        self.assertIn("[TYPE] approved", output)
        self.assertIn("[CHECK] approved", output)

    def test_inspect_tokens_prints_source_positions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.2\nspeak 1\n", encoding="utf-8")
            code, output, errors = self.run_cli("inspect", str(path), "--tokens")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("1:1 word newcode", output)
        self.assertIn("2:1 word speak", output)

    def test_inspect_ast_prints_program_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.2\nspeak 1\n", encoding="utf-8")
            code, output, errors = self.run_cli("inspect", str(path), "--ast")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("Program(statements=", output)
        self.assertIn("Speak(", output)

    def test_formatter_preserves_string_and_comment_text(self):
        source = (
            'newcode 0.2\n'
            '// keep leading marker\n'
            'verify 1 same 1\n'
            'speak "  text // inside string  " // trailing comment\n'
            'endverify\n'
        )

        formatted = format_source(source)

        self.assertIn('"  text // inside string  "', formatted)
        self.assertIn("// trailing comment", formatted)
        self.assertIn("    speak", formatted)

    def test_policy_check_reports_approval(self):
        code, output, errors = self.run_cli("policy", "check", "hello")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("GOODTHINK: text approved.", output)

    def test_policy_check_reports_prohibited_text(self):
        code, output, errors = self.run_cli("policy", "check", "freedom")

        self.assertEqual(code, 1)
        self.assertEqual(errors, "")
        self.assertIn("WORDCRIME:", output)

    def test_version_reports_language_and_runner_versions(self):
        code, output, errors = self.run_cli("version")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("goodthink 0.2.0 (Newcode 0.2)", output)

    def test_formatter_write_updates_file(self):
        source = "newcode 0.2\nverify 1 same 1\n    speak 1\nendverify\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(source, encoding="utf-8")
            code, output, errors = self.run_cli("format", str(path), "--write")

            self.assertEqual(code, 0)
            self.assertEqual(output, "")
            self.assertEqual(errors, "")
            self.assertEqual(path.read_text(encoding="utf-8"), format_source(source))

    def test_cli_requires_a_source_file(self):
        code, output, errors = self.run_cli("check")

        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertIn("source file is required", errors)

    def test_cli_check_returns_failure_and_source_location_for_invalid_program(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.think"
            path.write_text("newcode 0.2\nspeaknumber \"abc\"\n", encoding="utf-8")
            code, output, errors = self.run_cli("check", str(path))

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("invalid.think: line 2", errors)
        self.assertIn("THINKTYPE ERROR", errors)

    def test_cli_run_returns_success_for_real_program(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.2\nspeak 2 plus 3\n", encoding="utf-8")
            code, output, errors = self.run_cli("run", str(path))

        self.assertEqual(code, 0)
        self.assertIn("5\n", output)
        self.assertIn("GOODTHINK: program approved and completed.", output)
        self.assertEqual(errors, "")

    def test_cli_test_reports_zero_tests_when_program_has_no_testthink_block(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.2\nspeak 5\n", encoding="utf-8")
            code, output, errors = self.run_cli("test", str(path))

        self.assertEqual(code, 0)
        self.assertIn("GOODTHINK: 0 tests approved.", output)
        self.assertEqual(errors, "")


if __name__ == "__main__":
    unittest.main()
