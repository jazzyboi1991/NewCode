import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from newcode.cli import main


class Newcode05Tests(unittest.TestCase):
    def run_cli(self, source, command="run"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(source, encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main([command, str(path)])
        return code, output.getvalue(), errors.getvalue()

    def test_code_free_othercrime_catches_any_runtime_error(self):
        source = '''newcode 0.4
trythink
    speak 1 divide 0
othercrime
    speak "handled"
endtrythink
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("handled\n", output)

    def test_unknown_handler_code_is_rejected_during_check(self):
        source = '''newcode 0.5
trythink
    speak 1 divide 0
othercrime UNKNOWNCRIME
    speak "handled"
endtrythink
'''

        code, output, errors = self.run_cli(source, command="check")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("THINKLOGIC ERROR", errors)
        self.assertIn("UNKNOWNCRIME", errors)

    def test_duplicate_handler_code_is_rejected(self):
        source = '''newcode 0.5
trythink
    speak 1 divide 0
othercrime MATHCRIME
    speak "first"
othercrime MATHCRIME
    speak "second"
endtrythink
'''

        code, output, errors = self.run_cli(source, command="check")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("THINKLOGIC ERROR", errors)
        self.assertIn("MATHCRIME", errors)

    def test_catch_all_must_be_last(self):
        source = '''newcode 0.5
trythink
    speak 1 divide 0
othercrime
    speak "any"
othercrime MATHCRIME
    speak "specific"
endtrythink
'''

        code, output, errors = self.run_cli(source, command="check")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("THINKLOGIC ERROR", errors)
        self.assertIn("last", errors)

    def test_only_one_catch_all_is_allowed(self):
        source = '''newcode 0.5
trythink
    speak 1 divide 0
othercrime
    speak "first"
othercrime
    speak "second"
endtrythink
'''

        code, output, errors = self.run_cli(source, command="check")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("THINKLOGIC ERROR", errors)

    def test_worklimit_is_not_catchable(self):
        source = '''newcode 0.5
trythink
    speak 1
othercrime
endtrythink
'''

        with patch("newcode.runtime.MAX_STEPS", 1):
            code, output, errors = self.run_cli(source)

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("WORKLIMIT", errors)

    def test_handler_error_propagates_instead_of_falling_through(self):
        source = '''newcode 0.5
trythink
    speak 1 divide 0
othercrime MATHCRIME
    speak 1 divide 0
othercrime
    speak "outer"
endtrythink
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("MATHCRIME", errors)
        self.assertNotIn("outer", output)

    def test_all_runtime_handler_codes_are_accepted(self):
        for error_code in ("MATHCRIME", "INDEXCRIME", "FILECRIME", "INPUTCRIME", "WORDCRIME", "TESTCRIME"):
            with self.subTest(error_code=error_code):
                source = f'''newcode 0.5
trythink
    speak 1 divide 0
othercrime {error_code}
    speak "handled"
endtrythink
'''
                code, output, errors = self.run_cli(source, command="check")
                self.assertEqual(code, 0)
                self.assertEqual(errors, "")

    def test_nested_loop_control_stays_in_the_innermost_loop(self):
        source = '''newcode 0.5
thought numberthink outer be 0
thought numberthink inner be 0
repeatwhile outer less 2
    thought outer be outer plus 1
    repeatwhile inner less 1
        thought inner be inner plus 1
        stoprepeat
    endrepeat
endrepeat
speak outer, inner
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertEqual(output, "21\nGOODTHINK: program approved and completed.\n")


if __name__ == "__main__":
    unittest.main()
