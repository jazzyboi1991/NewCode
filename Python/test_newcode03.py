import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.runtime import Runtime
from newcode.validator import Validator
from newcode.cli import main


ROOT = Path(__file__).parent


def run(source, *, cwd=None):
    censor = Censor(ROOT / "prohibited_words.json")
    program = Parser(Lexer(source, censor).scan()).parse()
    routines = Validator(program).validate()
    output = io.StringIO()
    with redirect_stdout(output):
        Runtime(censor, routines, cwd=cwd).execute(program)
    return output.getvalue()


class Newcode03Tests(unittest.TestCase):
    def test_string_helpers(self):
        source = '''newcode 0.3
thought wordthink text be "banana"
speak length(text), ":", find(text, "nan"), ":", replace(text, "banana", "apple")
thought listthink parts be split(text, "a")
speak joinwords(parts, "-")
'''
        self.assertEqual(run(source), "6:2:apple\nb-n-n-\n")

    def test_multiline_string_and_extended_escape(self):
        source = 'newcode 0.3\nthought wordthink text be """first\\r\nsecond\\tline"""\nspeak text\n'
        self.assertEqual(run(source), "first\r\nsecond\tline\n")

    def test_nested_record_and_list_record_access(self):
        source = '''newcode 0.3
thought recordthink person be recordthink(profile be recordthink(name be "Ada"), scores be listthink(10, 20))
speak get person field profile, get get person field profile field name
'''
        self.assertEqual(run(source), "{name: Ada}Ada\n")

    def test_duplicate_record_field_is_rejected(self):
        source = 'newcode 0.3\nthought recordthink value be recordthink(name be "A", name be "B")\n'
        with self.assertRaises(NewcodeError) as caught:
            run(source)
        self.assertEqual(caught.exception.code, "CRIMESTOP")

    def test_missing_module_is_modulecrime(self):
        source = 'newcode 0.3\nuse mathgood from "missing.think"\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "main.think"
            path.write_text(source, encoding="utf-8")
            with self.assertRaises(NewcodeError) as caught:
                from newcode.cli import load
                load(path, Censor(ROOT / "prohibited_words.json"))
        self.assertEqual(caught.exception.code, "MODULECRIME")

    def test_cli_shortcuts_match_long_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text("newcode 0.3\nspeak 2 plus 3\n", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main([str(path)]), 0)
            self.assertIn("5\n", output.getvalue())


if __name__ == "__main__":
    unittest.main()
