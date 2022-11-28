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

        # todo: Determine when the \n appears and how to handle reliably
        self.assertEqual("Hello World!\n", outstream.getvalue())

    def test_input_output(self):
        code = ",++."

        instream = io.StringIO()
        instream.write('a')
        instream.seek(0)
        outstream = io.StringIO()

        bf.evaluate(code, instream=instream, outstream=outstream)

        self.assertEqual('c', outstream.getvalue())