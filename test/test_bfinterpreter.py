from unittest import TestCase
import io

import bfinterpreter.brainfuck as bf


class TestBFInterpreter(TestCase):
    def test_output(self):
        code = """
            ++++++++++[>+++++++>++++++++++>+++>+<<<<-]
            >++.>+.+++++++..+++.>++.<<+++++++++++++++.
            >.+++.------.--------.>+.>.
            """
        outstream = io.StringIO()
        bf.evaluate(code, outstream=outstream)
        self.assertEqual("Hello World!\n", outstream.getvalue())
