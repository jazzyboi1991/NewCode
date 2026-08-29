import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from newcode.censor import Censor
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.runtime import Runtime
from newcode.validator import Validator


ROOT = Path(__file__).parent


class HeaderlessProgramTests(unittest.TestCase):
    def test_headerless_02_program_runs(self):
        source = "thought numberthink count be 2\nspeak count plus 1\n"
        censor = Censor(ROOT / "prohibited_words.json")
        parser = Parser(Lexer(source, censor).scan())
        program = parser.parse()
        self.assertEqual(parser.version, "0.8")
        routines = Validator(program).validate()
        output = io.StringIO()
        with redirect_stdout(output):
            Runtime(censor, routines).execute(program)
        self.assertEqual(output.getvalue(), "3\n")


if __name__ == "__main__":
    unittest.main()
