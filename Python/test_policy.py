import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from newcode.censor import Censor
from newcode.cli import main
from newcode.errors import NewcodeError, Span


class PolicyTests(unittest.TestCase):
    LEXICON = Path(__file__).parent / "prohibited_words.json"

    def run_cli(self, source, command="run", input_value=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.think"
            path.write_text(source, encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            input_patch = patch("builtins.input", return_value=input_value) if input_value is not None else patch("builtins.input")
            with input_patch, redirect_stdout(output), redirect_stderr(errors):
                code = main([command, str(path)])
        return code, output.getvalue(), errors.getvalue()

    def test_official_lexicon_has_required_schema(self):
        raw = json.loads(self.LEXICON.read_text(encoding="utf-8"))

        self.assertIn("schema_version", raw)
        self.assertIn("normalization", raw)
        for key in ("replacement_rules", "prohibited_terms", "prohibited_phrases"):
            self.assertIsInstance(raw[key], list)
            self.assertTrue(raw[key])
        for item in raw["replacement_rules"]:
            self.assertTrue(item["term"])
            self.assertTrue(item["replacement"])
            self.assertTrue(item.get("category"))

    def test_replacement_rule_is_blocked_and_reports_approved_replacement(self):
        censor = Censor(self.LEXICON)

        with self.assertRaises(NewcodeError) as caught:
            censor.check("happy", False, Span(1, 1))

        self.assertEqual(caught.exception.code, "WORDCRIME")
        self.assertIn("Use 'good'", caught.exception.message)

    def test_prohibited_term_phrase_and_leetspeak_are_blocked(self):
        censor = Censor(self.LEXICON)

        for text in ("freedom", "very good", "fr33d0m", "free-dom"):
            with self.subTest(text=text):
                try:
                    censor.check(text, False, Span(1, 1))
                except NewcodeError as caught:
                    self.assertEqual(caught.code, "WORDCRIME")
                else:
                    self.fail("policy did not reject the text")

    def test_identifier_is_checked_during_lexing(self):
        code, output, errors = self.run_cli("newcode 0.5\nthought numberthink freedom be 1\n", "check")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("WORDCRIME", errors)

    def test_join_and_replace_results_are_rechecked(self):
        join_source = 'newcode 0.5\nspeak "free" join "dom"\n'
        replace_source = 'newcode 0.5\nspeak replace("good", "good", "freedom")\n'

        for source in (join_source, replace_source):
            with self.subTest(source=source):
                code, output, errors = self.run_cli(source)
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn("WORDCRIME", errors)

    def test_input_is_rechecked_when_listenwords_is_used(self):
        source = "newcode 0.5\nspeak listenwords\n"
        code, output, errors = self.run_cli(source, input_value="freedom")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("WORDCRIME", errors)

    def test_file_write_rechecks_content_immediately_before_saving(self):
        source = 'newcode 0.5\nwritefile "output.txt" be readfile "input.txt"\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            program = root / "program.think"
            program.write_text(source, encoding="utf-8")
            (root / "input.txt").write_text("freedom", encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main(["run", str(program)])

            self.assertEqual(code, 1)
            self.assertEqual(output.getvalue(), "")
            self.assertIn("WORDCRIME", errors.getvalue())
            self.assertFalse((root / "output.txt").exists())

    def test_comments_and_numbers_are_not_policy_checked(self):
        source = "newcode 0.5\n// freedom remains explanatory in a comment\nspeak 1984\n"
        code, output, errors = self.run_cli(source)

        self.assertEqual(code, 0)
        self.assertIn("1984", output)
        self.assertEqual(errors, "")

    def test_policy_document_is_tracked_at_repository_root(self):
        document = self.LEXICON.parent.parent / "Newcode Censorship Policy.md"

        self.assertTrue(document.is_file())
        contents = document.read_text(encoding="utf-8")
        self.assertIn("replacement_rules", contents)
        self.assertIn("WORDCRIME", contents)


if __name__ == "__main__":
    unittest.main()
