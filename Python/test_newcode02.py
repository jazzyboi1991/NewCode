import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.validator import Validator
from newcode.runtime import Runtime
from newcode.cli import load


ROOT = Path(__file__).parent


def run(source, *, cwd=None):
    censor = Censor(ROOT / "prohibited_words.json")
    program = Parser(Lexer(source, censor).scan()).parse()
    routines = Validator(program).validate()
    output = io.StringIO()
    with redirect_stdout(output):
        Runtime(censor, routines, cwd=cwd).execute(program)
    return output.getvalue()


class Newcode02Tests(unittest.TestCase):
    def test_mixed_list_and_index_operations(self):
        source = '''newcode 0.2
thought listthink values be listthink(1, "two", good)
change values at minus 1 be ungood
add 4 to values
speak size values, ":", get values at 1
'''
        self.assertEqual(run(source), '4:two\n')

    def test_record_and_map_missing_reads_return_nothink(self):
        source = '''newcode 0.2
thought recordthink person be recordthink(name be "Julia")
thought indexthink scores be indexthink("Julia" be 90)
change person field name be "Winston"
verify get person field score same nothink
    speak get scores key "Winston" same nothink
endverify
'''
        self.assertEqual(run(source), 'good\n')

    def test_foreach_and_string_slice(self):
        source = '''newcode 0.2
thought listthink values be listthink("ab", "cd")
foreach position, value in values
    speak position, slice value from 0 to 1
endforeach
'''
        self.assertEqual(run(source), '0a\n1c\n')

    def test_maybe_accepts_only_declared_type_or_nothink(self):
        source = 'newcode 0.2\nthought maybe numberthink score be nothink\nthought score be 4\nspeak score\n'
        self.assertEqual(run(source), '4\n')

    def test_file_rawthink_is_censored_when_spoken(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "input.txt").write_text("freedom", encoding="utf-8")
            source = 'newcode 0.2\nthought rawthink text be readfile "input.txt"\nspeak text\n'
            with self.assertRaises(NewcodeError) as caught:
                run(source, cwd=root)
            self.assertEqual(caught.exception.code, "WORDCRIME")

    def test_module_routine_is_namespaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "math.think").write_text(
                "newcode 0.2\nroutine numberthink addgood(numberthink first, numberthink second)\n    reportvalue first plus second\nendroutine\n",
                encoding="utf-8",
            )
            source = 'newcode 0.2\nuse mathgood from "math.think"\nspeak call mathgood addgood(2, 3)\n'
            censor = Censor(ROOT / "prohibited_words.json")
            Parser(Lexer(source, censor).scan()).parse()
            routines = {"mathgood." + routine.name: routine for routine in load(root / "math.think", censor)}
            self.assertIn("mathgood.addgood", routines)

    def test_trythink_routes_runtime_error(self):
        source = '''newcode 0.2
trythink
    speak 1 divide 0
othercrime MATHCRIME
    speak "handled"
endtrythink
'''
        self.assertEqual(run(source), 'handled\n')


if __name__ == "__main__":
    unittest.main()
