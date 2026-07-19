from __future__ import annotations

import unittest
from pathlib import Path

from newcodespeak.censor import censor_source, line_and_column
from newcodespeak.errors import ApprovalDeclarationError, CensorshipError

TEST_PATH = Path("program.ncs")


class CensorTests(unittest.TestCase):
    def test_approved_user_name_and_core_words_pass(self) -> None:
        result = censor_source("approve quota; set quota to 1;", TEST_PATH)

        self.assertEqual(result.user_names, frozenset({"quota"}))

    def test_core_word_needs_no_user_approval(self) -> None:
        result = censor_source("approve quota; proclaim doubleplusgood;", TEST_PATH)

        self.assertEqual(result.user_names, frozenset({"quota"}))

    def test_unapproved_code_word_is_rejected_with_location(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source("approve quota; set memory to 1;", TEST_PATH)

        error = raised.exception
        self.assertEqual(error.word, "memory")
        self.assertEqual((error.line, error.column), (1, 20))

    def test_unapproved_word_in_string_is_rejected(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source('approve quota; proclaim "doubt";', TEST_PATH)

        self.assertEqual(raised.exception.word, "doubt")

    def test_unapproved_word_in_comment_is_rejected(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source("approve quota; // past", TEST_PATH)

        self.assertEqual(raised.exception.word, "past")

    def test_missing_first_approval_is_rejected(self) -> None:
        with self.assertRaises(ApprovalDeclarationError):
            censor_source("set quota to 1;", TEST_PATH)

    def test_declaration_must_be_the_first_statement(self) -> None:
        with self.assertRaises(ApprovalDeclarationError):
            censor_source("set quota to 1; approve quota;", TEST_PATH)

    def test_invalid_user_names_are_rejected(self) -> None:
        for name in ("Upper", "quota2", "quota-name", "할당량"):
            with self.subTest(name=name):
                with self.assertRaises(ApprovalDeclarationError):
                    censor_source(f"approve {name};", TEST_PATH)

    def test_empty_duplicate_and_core_names_are_rejected(self) -> None:
        invalid_sources = (
            "approve quota,;",
            "approve quota, quota;",
            "approve party;",
        )

        for source in invalid_sources:
            with self.subTest(source=source):
                with self.assertRaises(ApprovalDeclarationError):
                    censor_source(source, TEST_PATH)

    def test_numbers_are_not_vocabulary_words(self) -> None:
        censor_source("approve quota; set quota to 1984;", TEST_PATH)

    def test_line_and_column_are_one_based(self) -> None:
        self.assertEqual(line_and_column("one\ntwo", 4), (2, 1))


if __name__ == "__main__":
    unittest.main()
