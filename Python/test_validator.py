import unittest
from pathlib import Path

from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.validator import Validator


ROOT = Path(__file__).parent


def validate(source):
    censor = Censor(ROOT / "prohibited_words.json")
    program = Parser(Lexer(source, censor).scan()).parse()
    return Validator(program).validate()


class ValidatorTests(unittest.TestCase):
    def test_non_silent_routine_requires_reportvalue(self):
        source = '''newcode 0.2
routine numberthink calculate()
endroutine
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKLOGIC ERROR")

    def test_routine_reportvalue_must_match_declared_type(self):
        source = '''newcode 0.2
routine numberthink calculate()
    reportvalue "abc"
endroutine
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_repeat_control_is_rejected_outside_repeatwhile(self):
        source = "newcode 0.2\nnextrepeat\n"
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "CRIMESTOP")

    def test_foreach_variables_do_not_escape_loop_scope(self):
        source = '''newcode 0.2
thought listthink values be listthink(1)
foreach position, value in values
    speak value
endforeach
speak value
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "CRIMESTOP")

    def test_duplicate_global_names_are_rejected(self):
        source = '''newcode 0.2
thought numberthink value be 1
thought numberthink value be 2
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "CRIMESTOP")

    def test_composite_assignment_requires_declared_type(self):
        source = '''newcode 0.2
thought listthink values be listthink(1)
thought values be "abc"
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_verify_requires_goodthink_condition(self):
        source = '''newcode 0.2
verify 1
    speak "abc"
endverify
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_routine_cannot_read_global_variables(self):
        source = '''newcode 0.2
thought numberthink total be 1
routine numberthink calculate()
    reportvalue total
endroutine
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "CRIMESTOP")

    def test_routine_call_argument_count_is_checked(self):
        source = '''newcode 0.2
routine numberthink sumgood(numberthink left, numberthink right)
    reportvalue left plus right
endroutine
speak sumgood(1)
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_routine_call_argument_type_is_checked(self):
        source = '''newcode 0.2
routine numberthink sumgood(numberthink left, numberthink right)
    reportvalue left plus right
endroutine
speak sumgood(1, "abc")
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_recursive_routine_is_rejected(self):
        source = '''newcode 0.2
routine numberthink loop(numberthink value)
    reportvalue loop(value)
endroutine
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "LOOPTHINK")

    def test_add_requires_listthink(self):
        source = '''newcode 0.2
thought numberthink value be 1
add 2 to value
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_remove_requires_compound_value(self):
        source = '''newcode 0.2
thought numberthink value be 1
remove value at 0
'''
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_speaknumber_requires_numberthink(self):
        source = 'newcode 0.2\nspeaknumber "abc"\n'
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")

    def test_precision_argument_requires_numberthink(self):
        source = 'newcode 0.2\nspeak 1 to "abc"\n'
        with self.assertRaises(NewcodeError) as caught:
            validate(source)
        self.assertEqual(caught.exception.code, "THINKTYPE ERROR")


if __name__ == "__main__":
    unittest.main()
