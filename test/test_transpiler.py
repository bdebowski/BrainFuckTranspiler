from unittest import TestCase
import io

from transpiler.transpiler import Transpiler
import bfinterpreter.brainfuck as bf


class TestTranspiler(TestCase):
    def test_var_read_msg_comment(self):
        code = """
            var X//This is a comment
            read X--This is also a comment
            msg "Bye" X#No doubt it is a comment
            rem &&Some comment~!@#$":<
            """
        provided_input = '?'
        required_output = 'Bye?'

        instream = io.StringIO()
        instream.write(provided_input)
        instream.seek(0)
        outstream = io.StringIO()

        bf.evaluate(Transpiler().transpile(code), instream=instream, outstream=outstream)

        self.assertEqual(required_output, outstream.getvalue())
