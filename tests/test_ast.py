from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from newcodespeak.ast import (
    Approval,
    Assignment,
    BinaryExpression,
    IntegerLiteral,
    NameReference,
    Program,
)


class AstTests(unittest.TestCase):
    def test_program_can_describe_an_assignment(self) -> None:
        program = Program(
            approval=Approval(("quota",)),
            statements=(
                Assignment(
                    name="quota",
                    expression=BinaryExpression(
                        left=NameReference("quota"),
                        operator="minus",
                        right=IntegerLiteral(1),
                    ),
                ),
            ),
        )

        self.assertEqual(program.approval.names, ("quota",))
        self.assertEqual(program.statements[0].name, "quota")

    def test_nodes_are_immutable(self) -> None:
        literal = IntegerLiteral(1)

        with self.assertRaises(FrozenInstanceError):
            literal.value = 2


if __name__ == "__main__":
    unittest.main()
