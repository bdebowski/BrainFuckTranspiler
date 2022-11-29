from unittest import TestCase
import io

from transpiler.transpiler import Transpiler
import bfinterpreter.brainfuck as bf


class TestTranspilerBasicFunctionality(TestCase):
    def _check_output(self, code, provided_input='', required_output=''):
        instream = io.StringIO()
        instream.write(provided_input)
        instream.seek(0)

        outstream = io.StringIO()

        bf.evaluate(Transpiler().transpile(code), instream=instream, outstream=outstream)

        self.assertEqual(required_output, outstream.getvalue())

    def test_var_read_msg_comment(self):
        self._check_output(
            """
            var X//This is a comment
            read X--This is also a comment
            msg "Bye" X#No doubt it is a comment
            rem &&Some comment~!@#$":<""",
            provided_input='?',
            required_output='Bye?')

    def test_set_inc_dec(self):
        self._check_output(
            """
            var A B
            sEt A 'a'
            msg a B
            set B 50
            msG A b
            inc A 10
            dec B -20
            msg A B
            """,
            provided_input='',
            required_output='a\0a2kF')

    def test_kinds_of_numbers(self):
        self._check_output(
            """
            var X
            set X  114514
            msg X
            set X -114514
            msg X
            set X 'X'
            msg X
            """,
            provided_input='',
            required_output='\x52\xae\x58')

    def test_add_sub_mul(self):
        self._check_output(
            """
            var A B C
            read A
            read B
            add a b c
            msg a b c
            sub a b a
            msg a b c
            mul b a c
            msg a b c
            """,
            provided_input='0\x07',
            required_output='\x30\x07\x37\x29\x07\x37\x29\x07\x1f')

    def test_divmod_div_mod(self):
        self._check_output(
            """
            var A B C D
            set A 79
            set B 13
            divmod A B C D
            msg A B C D
            div C D C
            msg A B C D
            mod A D A
            msg A B C D
            """,
            provided_input='',
            required_output='\x4f\x0d\x06\x01\x4f\x0d\x06\x01\x00\x0d\x06\x01')

    def test_cmp(self):
        self._check_output(
            """
            var X K
            read X
            cmp 80 X K
            msg X K
            cmp X 'z' K
            msg X K
            cmp X X K
            msg X K
            """,
            provided_input='\x80',
            required_output='\x80\xff\x80\x01\x80\x00')

    def test_a2b_b2a(self):
        self._check_output(
            """
            var A B C D
            set a 247
            b2a A B C D
            msg A B C D
            inc B 1
            dec C 2
            inc D 5
            a2b B C D A
            msg A B C D // A = (100 * (2 + 1) + 10 * (4 - 2) + (7 + 5)) % 256 = 76 = 0x4c
            """,
            provided_input='',
            required_output='\xf7\x32\x34\x37\x4c\x33\x32\x3c')

    def test_lset_lget(self):
        self._check_output(
            """
            var L  [ 20 ]  I X
            lset L 10 80
            set X 20
            lset L 5 X
            set X 9
            lset L X X
            set I 4
            lget L I X
            msg X
            lget L 5 X
            msg X
            lget L 9 X
            msg X
            lget L 10 X
            msg X
            lget L 19 X
            msg X
            """,
            provided_input='',
            required_output='\x00\x14\x09\x50\x00')

    def test_ifeq_ifneq_wneq(self):
        self._check_output(
            """
            var F L[5] X
            set F 0
            add 10 10 X
            wneq F 5
                lset L F X
                inc F 1
                dec X 1
            end
            //L == [20,19,18,17,16]
    
            wneq F 0
                inc F -1
                lget L F X
                msg X
            end
    
            set F 10
            wneq F 0
                ifeq F 10
                    set F 5
                end
                dec F 1
                lget L F X
                ifneq X 18
                    msg F X
                end
            end
            ifeq F 0
                ifneq X 50
                    msg ";-)"
                end
            end
            """,
            provided_input='',
            required_output='\x10\x11\x12\x13\x14\x04\x10\x03\x11\x01\x13\x00\x14;-)')

    def test_proc(self):
        self._check_output(
            """
            var A B T
            set A 'U'
            set B 'V'
    
            msg"Outer Before : "A B"\\n"
            call swap B A
            msg"Outer After : "A B"\\n"
    
            proc swap x y
                msg "Inner Before : "x y"\\n"
                set T x
                call say T
                set x y
                set y T
                msg "Inner After : "x y"\\n"
            end
            proc say x
                msg "It is " x " now\\n"
            end
            """,
            provided_input='',
            required_output=
            'Outer Before : UV\n' +
            'Inner Before : VU\n' +
            'It is V now\n' +
            'Inner After : UV\n' +
            'Outer After : VU\n')
