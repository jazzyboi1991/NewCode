from pathlib import Path
import unittest
from newcodespeak import ast
from newcodespeak.lexer import lex_source
from newcodespeak.parser import parse_tokens

class ParserTests(unittest.TestCase):
    def parse(self, source: str) -> ast.Program:
        return parse_tokens(lex_source(source, Path("test.ncs")), Path("test.ncs"))
    def test_program(self) -> None:
        program=self.parse("approve quota; set quota to quota minus 1;")
        self.assertEqual(program.approval.names,("quota",))
        self.assertIsInstance(program.statements[0],ast.Assignment)
    def test_fact_rule_and_query(self) -> None:
        program=self.parse("approve quota; fact citizen is good; rule citizen obey party when citizen is good; query citizen obey party;")
        self.assertEqual([type(x) for x in program.statements],[ast.Fact,ast.Rule,ast.Query])
    def test_blocks(self) -> None:
        program=self.parse("approve quota; repeat while quota above 0 proclaim good; set quota to quota minus 1; end")
        self.assertIsInstance(program.statements[0],ast.Repetition)

