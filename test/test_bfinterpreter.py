from unittest import TestCase
import io

import bfinterpreter.brainfuck as bf


class TestBFInterpreter(TestCase):
    def test_output(self):
        # Outputs "Hello World!\n"
        code = """
            ++++++++++[>+++++++>++++++++++>+++>+<<<<-]
            >++.>+.+++++++..+++.>++.<<+++++++++++++++.
            >.+++.------.--------.>+.>.
            """

        outstream = io.StringIO()

        bf.evaluate(code, outstream=outstream)

        self.assertEqual("Hello World!\n", outstream.getvalue())

    def test_input_output(self):
        # Reads two input chars and outputs them incremented by two
        code = ",++>,++<.>."

        instream = io.StringIO()
        instream.write('axNOTUSED')
        instream.seek(0)
        outstream = io.StringIO()

        bf.evaluate(code, instream=instream, outstream=outstream)

        self.assertEqual('cz', outstream.getvalue())
