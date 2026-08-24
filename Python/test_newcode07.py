import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from newcode.cli import main, namespace_routine
from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.runtime import Runtime
from newcode.standard import standard_module
from newcode.validator import Validator


class CommandthinkTests(unittest.TestCase):
    def run_program(self, source, argv=()):
        censor = Censor(Path(__file__).parent / "prohibited_words.json")
        program = Parser(Lexer(source, censor).scan()).parse()
        program.statements.extend(
            namespace_routine(routine, "commandthink")
            for routine in standard_module("standard/commandthink.think").values()
        )
        routines = Validator(program).validate()
        output = io.StringIO()
        with redirect_stdout(output):
            Runtime(censor, routines, argv=list(argv)).execute(program)
        return output.getvalue()

    def test_arguments_returns_arguments_after_separator(self):
        source = '''
newcode 0.7
use commandthink from "standard/commandthink.think"
speak call commandthink arguments()
'''
        self.assertEqual(self.run_program(source, ["one", "two"]), "[one, two]\n")

    def test_argument_uses_zero_based_index(self):
        source = '''
newcode 0.7
use commandthink from "standard/commandthink.think"
speak call commandthink argument(0), call commandthink argument(1)
'''
        self.assertEqual(self.run_program(source, ["first", "second"]), "firstsecond\n")

    def test_argument_out_of_range_is_inputcrime(self):
        source = '''
newcode 0.7
use commandthink from "standard/commandthink.think"
speak call commandthink argument(1)
'''
        with self.assertRaises(NewcodeError) as context:
            self.run_program(source, ["only"])
        self.assertEqual(context.exception.code, "INPUTCRIME")

    def test_argument_requires_integer_number(self):
        source = '''
newcode 0.7
use commandthink from "standard/commandthink.think"
speak call commandthink argument(1.5)
'''
        with self.assertRaises(NewcodeError) as context:
            self.run_program(source, ["only"])
        self.assertEqual(context.exception.code, "THINKLOGIC ERROR")

    def test_command_arguments_are_checked_by_policy(self):
        source = '''
newcode 0.7
use commandthink from "standard/commandthink.think"
speak call commandthink arguments()
'''
        with self.assertRaises(NewcodeError) as context:
            self.run_program(source, ["freedom"])
        self.assertEqual(context.exception.code, "WORDCRIME")

    def test_cli_passes_arguments_after_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(
                'newcode 0.7\nuse commandthink from "standard/commandthink.think"\nspeak call commandthink argument(0)\n',
                encoding="utf-8",
            )
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main(["run", str(path), "--", "hello"])
        self.assertEqual(code, 0)
        self.assertIn("hello\n", output.getvalue())
        self.assertEqual(errors.getvalue(), "")

    def test_cli_filename_shortcut_passes_arguments_after_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(
                'newcode 0.7\nuse commandthink from "standard/commandthink.think"\nspeak call commandthink argument(0)\n',
                encoding="utf-8",
            )
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main([str(path), "--", "shortcut"])
        self.assertEqual(code, 0)
        self.assertIn("shortcut\n", output.getvalue())
        self.assertEqual(errors.getvalue(), "")

    def test_official_censor_reads_bundled_lexicon(self):
        from newcode.censor import Censor
        self.assertGreater(len(Censor.official().terms), 0)


if __name__ == "__main__":
    unittest.main()
