import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from newcode.cli import main


class Newcode06Tests(unittest.TestCase):
    def run_cli(self, source, command="run", extra_files=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "program.think"
            path.write_text(source, encoding="utf-8")
            for name, content in (extra_files or {}).items():
                (root / name).write_text(content, encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main([command, str(path)])
        return code, output.getvalue(), errors.getvalue()

    def test_named_record_type_can_be_created_read_and_changed(self):
        source = '''newcode 0.6
recordthink Person
    thought wordthink name
    thought numberthink age
endrecordthink
thought Person user be Person(name be "Ada", age be 30)
speak get user field name
change user field age be 31
speak get user field age
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("Ada\n", output)
        self.assertIn("31\n", output)

    def test_named_record_constructor_is_independent_of_field_order(self):
        source = '''newcode 0.6
recordthink Person
    thought wordthink name
    thought numberthink age
endrecordthink
thought Person user be Person(age be 30, name be "Ada")
speak get user field name
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("Ada\n", output)

    def test_nested_custom_records_lists_and_maybe_values_are_supported(self):
        source = '''newcode 0.6
recordthink Address
    thought wordthink city
endrecordthink
recordthink Person
    thought wordthink name
    thought Address address
    thought maybe numberthink score
endrecordthink
thought Person user be Person(name be "Ada", address be Address(city be "Seoul"), score be nothink)
thought listthink people be listthink(user)
speak get get user field address field city
speak size people
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("Seoul\n", output)
        self.assertIn("1\n", output)

    def test_missing_unknown_duplicate_and_wrong_type_fields_are_rejected(self):
        cases = (
            ('Person(name be "Ada")', "missing field"),
            ('Person(name be "Ada", age be 30, extra be 1)', "unknown field"),
            ('Person(name be "Ada", name be "Grace", age be 30)', "duplicate field"),
            ('Person(name be 7, age be 30)', "wrong field type"),
        )
        prefix = '''newcode 0.6
recordthink Person
    thought wordthink name
    thought numberthink age
endrecordthink
thought Person user be '''

        for expression, label in cases:
            with self.subTest(label=label):
                code, output, errors = self.run_cli(prefix + expression + "\n", "check")
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn("THINK", errors)

    def test_unknown_type_and_name_collisions_use_existing_errors(self):
        unknown = "newcode 0.6\nthought Missing user be nothink\n"
        collision = '''newcode 0.6
recordthink Person
    thought wordthink name
endrecordthink
recordthink Person
    thought wordthink other
endrecordthink
'''

        code, _, errors = self.run_cli(unknown, "check")
        self.assertEqual(code, 1)
        self.assertIn("THINKTYPE ERROR", errors)
        code, _, errors = self.run_cli(collision, "check")
        self.assertEqual(code, 1)
        self.assertIn("CRIMESTOP", errors)

    def test_field_access_and_change_errors_use_existing_codes(self):
        missing_access = '''newcode 0.6
recordthink Person
    thought wordthink name
endrecordthink
thought Person user be Person(name be "Ada")
speak get user field age
'''
        wrong_change = '''newcode 0.6
recordthink Person
    thought wordthink name
endrecordthink
thought Person user be Person(name be "Ada")
change user field name be 7
'''

        code, _, errors = self.run_cli(missing_access, "check")
        self.assertEqual(code, 1)
        self.assertIn("INDEXCRIME", errors)
        code, _, errors = self.run_cli(wrong_change, "check")
        self.assertEqual(code, 1)
        self.assertIn("THINKTYPE ERROR", errors)

    def test_record_type_declaration_is_not_allowed_inside_a_module(self):
        source = 'newcode 0.6\nuse library from "library.think"\n'
        module = '''newcode 0.6
recordthink Person
    thought wordthink name
endrecordthink
'''

        code, output, errors = self.run_cli(source, "check", {"library.think": module})

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("MODULECRIME", errors)

    def test_headerless_program_uses_newcode_06(self):
        source = '''recordthink Person
    thought wordthink name
endrecordthink
thought Person user be Person(name be "Ada")
speak get user field name
'''

        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertIn("Ada\n", output)


if __name__ == "__main__":
    unittest.main()
