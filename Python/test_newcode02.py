import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.validator import Validator
from newcode.runtime import Runtime
from newcode.cli import load
from newcode.model import Program


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

    def test_list_index_out_of_range_is_indexcrime(self):
        source = '''newcode 0.2
thought listthink values be listthink(1, 2)
speak get values at 2
'''
        with self.assertRaises(NewcodeError) as caught:
            run(source)
        self.assertEqual(caught.exception.code, "INDEXCRIME")

    def test_negative_list_index_reads_from_end(self):
        source = '''newcode 0.2
thought listthink values be listthink("first", "last")
speak get values at minus 1
'''
        self.assertEqual(run(source), "last\n")

    def test_file_path_escape_is_filecrime(self):
        source = 'newcode 0.2\nspeak readfile "../outside.txt"\n'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(NewcodeError) as caught:
                run(source, cwd=Path(directory))
        self.assertEqual(caught.exception.code, "FILECRIME")

    def test_maybe_rejects_value_of_the_wrong_type(self):
        source = 'newcode 0.2\nthought maybe numberthink score be nothink\nthought score be "abc"\n'
        with self.assertRaises(NewcodeError) as caught:
            run(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_lines_and_joinlines_round_trip_file_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "input.txt").write_text("one\ntwo\n", encoding="utf-8")
            source = '''newcode 0.2
thought rawthink text be readfile "input.txt"
thought listthink parts be lines text
speak joinlines parts
'''
            self.assertEqual(run(source, cwd=root), "one\ntwo\n")

    def test_foreach_visits_index_map_key_and_value(self):
        source = '''newcode 0.2
thought indexthink scores be indexthink("Julia" be 90, "Winston" be 80)
foreach person, score in scores
    speak person, ":", score
endforeach
'''
        self.assertEqual(run(source), "Julia:90\nWinston:80\n")

    def test_writefile_and_appendfile_update_relative_text_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = '''newcode 0.2
writefile "output.txt" be "one"
appendfile "output.txt" be " two"
'''
            self.assertEqual(run(source, cwd=root), "")
            self.assertEqual((root / "output.txt").read_text(encoding="utf-8"), "one two")

    def test_cyclic_module_import_is_loopthink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "first.think").write_text(
                'newcode 0.2\nuse second from "second.think"\n', encoding="utf-8"
            )
            (root / "second.think").write_text(
                'newcode 0.2\nuse first from "first.think"\n', encoding="utf-8"
            )
            censor = Censor(ROOT / "prohibited_words.json")
            with self.assertRaises(NewcodeError) as caught:
                load(root / "first.think", censor)
        self.assertEqual(caught.exception.code, "LOOPTHINK")

    def test_module_rejects_top_level_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / "bad.think"
            module.write_text('newcode 0.2\nspeak "abc"\n', encoding="utf-8")
            censor = Censor(ROOT / "prohibited_words.json")
            with self.assertRaises(NewcodeError) as caught:
                load(module, censor)
        self.assertEqual(caught.exception.code, "MODULECRIME")

    def test_test_mode_blocks_input_and_file_writes(self):
        source = '''newcode 0.2
testthink "isolated"
    writefile "output.txt" be "abc"
endtestthink
'''
        censor = Censor(ROOT / "prohibited_words.json")
        program = Parser(Lexer(source, censor).scan()).parse()
        routines = Validator(program).validate()
        test = next(statement for statement in program.statements if statement.__class__.__name__ == "TestThink")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(NewcodeError) as caught:
                Runtime(censor, routines, cwd=directory, test_mode=True).execute(Program(test.body))
        self.assertEqual(caught.exception.code, "TESTCRIME")

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

    def test_trythink_rethrows_unhandled_runtime_error(self):
        source = '''newcode 0.2
trythink
    speak 1 divide 0
othercrime INDEXCRIME
    speak "handled"
endtrythink
'''
        with self.assertRaises(NewcodeError) as caught:
            run(source)
        self.assertEqual(caught.exception.code, "MATHCRIME")

    def test_arithmetic_and_precision_output(self):
        source = '''newcode 0.2
speak 1 plus 2, 5 minus 1, 2 times 3, 8 divide 2, 1 divide 3 to 2
'''
        self.assertEqual(run(source), "34640.33\n")

    def test_repeatwhile_nextrepeat_and_stoprepeat(self):
        source = '''newcode 0.2
thought numberthink count be 0
repeatwhile count less 5
    thought count be count plus 1
    verify count same 2
        nextrepeat
    endverify
    verify count same 4
        stoprepeat
    endverify
endrepeat
speak count
'''
        self.assertEqual(run(source), "4\n")

    def test_number_and_word_input_are_converted(self):
        number_source = "newcode 0.2\nspeak listennumber\n"
        word_source = "newcode 0.2\nspeak listenwords\n"
        with patch("builtins.input", return_value="minus 2.5"):
            self.assertEqual(run(number_source), "-2.5\n")
        with patch("builtins.input", return_value="hello"):
            self.assertEqual(run(word_source), "hello\n")

    def test_invalid_number_input_is_inputcrime(self):
        source = "newcode 0.2\nspeak listennumber\n"
        with patch("builtins.input", return_value="not-a-number"):
            with self.assertRaises(NewcodeError) as caught:
                run(source)
        self.assertEqual(caught.exception.code, "INPUTCRIME")

    def test_missing_file_is_filecrime(self):
        source = 'newcode 0.2\nspeak readfile "missing.txt"\n'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(NewcodeError) as caught:
                run(source, cwd=Path(directory))
        self.assertEqual(caught.exception.code, "FILECRIME")


if __name__ == "__main__":
    unittest.main()
