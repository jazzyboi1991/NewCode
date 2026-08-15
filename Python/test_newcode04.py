import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from newcode.cli import main
from newcode.censor import Censor
from newcode.errors import NewcodeError, Span
from newcode.runtime import Runtime
from newcode.standard import standard_module


class Newcode04Tests(unittest.TestCase):
    def run_cli(self, source, command="run", files=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(source, encoding="utf-8")
            for name, content in (files or {}).items():
                target = Path(directory) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main([command, str(path)])
        return code, output.getvalue(), errors.getvalue()

    def test_randomthink_import_and_seeded_number(self):
        source = '''newcode 0.4
use randomthink from "standard/randomthink.think"
call randomthink setseed(1984)
speak call randomthink randomnumber(1, 6)
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("3\n", output)

    def test_randomfraction_returns_a_fraction_in_its_documented_range(self):
        source = '''newcode 0.4
use randomthink from "standard/randomthink.think"
call randomthink setseed(1984)
thought numberthink value be call randomthink randomfraction()
speak value more 0 both value less 1
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("good\n", output)

    def test_timethink_returns_local_time_record_and_epoch_seconds(self):
        source = '''newcode 0.4
use timethink from "standard/timethink.think"
thought recordthink current be call timethink currenttime()
thought numberthink count be call timethink timecount()
speak current, count
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("{year:", output)
        self.assertRegex(output, r"}\d+\n")

    def test_timethink_uses_injectable_clock_for_repeatable_runtime_tests(self):
        fixed_now = datetime(1984, 4, 4, 12, 30, 15, tzinfo=timezone.utc)
        runtime = Runtime(
            Censor(Path(__file__).parent / "prohibited_words.json"),
            {},
            now_provider=lambda: fixed_now,
            time_provider=lambda: 123.9,
        )
        routines = standard_module("standard/timethink.think")

        current = routines["currenttime"].handler(runtime, [], None)
        count = routines["timecount"].handler(runtime, [], None)

        self.assertEqual(current["year"], Fraction(1984))
        self.assertEqual(current["second"], Fraction(15))
        self.assertEqual(count, Fraction(123))

    def test_paththink_joins_and_inspects_safe_existing_files(self):
        source = '''newcode 0.4
use paththink from "standard/paththink.think"
thought wordthink full be call paththink joinpath("reports", "today.txt")
speak full, call paththink filename(full), call paththink extension(full), call paththink parentpath(full), call paththink pathexists(full)
'''

        code, output, errors = self.run_cli(source, files={"reports/today.txt": "approved"})

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("reports/today.txttoday.txttxtreportsgood\n", output)

    def test_file_commands_share_paththink_backslash_rejection(self):
        source = 'newcode 0.4\nspeak readfile "folder\\\\inside.txt"\n'

        code, output, errors = self.run_cli(source, files={"folder\\inside.txt": "approved"})

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("FILECRIME", errors)

    def test_standard_module_errors_keep_existing_error_codes(self):
        cases = (
            ('use randomthink from "standard/randomthink.think"\nspeak call randomthink randomnumber("one", 2)\n', "THINKTYPE ERROR"),
            ('use randomthink from "standard/randomthink.think"\nspeak call randomthink randomnumber(2, 1)\n', "THINKLOGIC ERROR"),
            ('use randomthink from "standard/randomthink.think"\ncall randomthink setseed(1.5)\n', "THINKLOGIC ERROR"),
            ('use missingthink from "standard/missing.think"\n', "MODULECRIME"),
        )

        for statements, error_code in cases:
            with self.subTest(error_code=error_code):
                code, output, errors = self.run_cli("newcode 0.4\n" + statements)
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn(error_code, errors)

    def test_testthink_can_call_standard_routines(self):
        source = '''newcode 0.4
use randomthink from "standard/randomthink.think"
testthink "seeded standard routine"
    call randomthink setseed(1984)
    speak call randomthink randomnumber(1, 6)
endtestthink
'''

        code, output, errors = self.run_cli(source, command="test")

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("3\n", output)
        self.assertIn("1 tests approved", output)

    def test_paththink_rechecks_generated_words_against_the_policy(self):
        runtime = Runtime(Censor(Path(__file__).parent / "prohibited_words.json"), {})
        joinpath = standard_module("standard/paththink.think")["joinpath"]

        with self.assertRaises(NewcodeError) as caught:
            joinpath.handler(runtime, ["reports", "freedom.txt"], Span(1, 1))

        self.assertEqual(caught.exception.code, "WORDCRIME")

    def test_standard_module_alias_collision_is_rejected(self):
        source = '''newcode 0.4
use randomthink from "standard/randomthink.think"
use randomthink from "standard/randomthink.think"
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("CRIMESTOP", errors)

    def test_user_module_can_call_its_imported_standard_module(self):
        source = '''newcode 0.4
use helperthink from "helper.think"
speak call helperthink roll()
'''
        helper = '''newcode 0.4
use randomthink from "standard/randomthink.think"
routine numberthink roll()
    call randomthink setseed(1984)
    reportvalue call randomthink randomnumber(1, 6)
endroutine
'''

        code, output, errors = self.run_cli(source, files={"helper.think": helper})

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("3\n", output)


if __name__ == "__main__":
    unittest.main()
