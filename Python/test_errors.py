import unittest

from newcode.errors import NewcodeError, Span


class ErrorTests(unittest.TestCase):
    def test_display_includes_filename_source_line_and_pointer(self):
        error = NewcodeError("WORDCRIME", "prohibited word", Span(2, 7))
        rendered = error.display("program.think", "newcode 0.2\nspeak freedom\n")

        self.assertIn("program.think: line 2, column 7", rendered)
        self.assertIn("speak freedom", rendered)
        self.assertIn("      ^", rendered)

    def test_display_without_a_matching_source_line_keeps_header(self):
        error = NewcodeError("THINKLOGIC ERROR", "bad source", Span(4, 1))

        self.assertEqual(
            error.display("program.think", "newcode 0.2\n"),
            "program.think: line 4, column 1: THINKLOGIC ERROR: bad source",
        )
