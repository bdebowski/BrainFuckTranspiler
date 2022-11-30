from unittest import TestCase

from transpiler.transpiler import clean_and_normalize


class TestTranspilerParsing(TestCase):
    def test_clean_and_normalize(self):
        code = """
            REM This is a comment
            VAR i l[10] x y // another comment
            VAR A B
            sub a b--a comment#and a comment
            msg "This // is not a comment"--but this is "what"
            """
        required_result = "var i l[10] x y var a b sub a b msg \"This // is not a comment\""

        self.assertEqual(required_result, clean_and_normalize(code))
