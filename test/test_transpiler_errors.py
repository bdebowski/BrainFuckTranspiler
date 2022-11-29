from unittest import TestCase

from transpiler.transpiler import Transpiler


class TestTranspilerBasicFunctionality(TestCase):
    def test_error_unknown_instruction(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var a
            mov a 5
            """)

    def test_error_args_count(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var x
            set x
            """)

    def test_error_undefined_var_names(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            msg x
            """)

    def test_error_duplicate_var_names(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var Q
            var q[20]
            """)

    def test_error_var_define_in_proc(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            proc nice
                var evil
            end
            """)

    def test_error_unmatched_braces(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var x[60 Y
            """)

    def test_error_var_required_got_other(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var c 20
            set 20 20
            add "what" 'x' c
            // all lines above result in this error respectively
            """)

    def test_error_var_required_got_list(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var L[40] X[20]
            LSet L 0 X
            """)

    def test_error_list_required_got_var(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var L X
            LGet L 0 X
            """)

    def test_error_unmatched_single_quotes(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var x
            set x 'z
            """)

    def test_error_unmatched_double_quotes(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            msg " nope
            """)

    def test_error_nested_procedure(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            proc a
            proc b
            end
            end
            """)

    def test_error_duplicate_procedure_names(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            proc Q a
            end
            proc Q q
            end
            """)

    def test_error_duplicate_param_names(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            proc Q q Q
            end
            """)

    def test_error_end_wo_starting_block(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            end
            msg " That's end"
            """)

    def test_error_unclosed_block(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var a
            set a 20
            ifeq a 19
            msg "eq"
            """)

    def test_error_undefined_procedure(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var Yes
            caLL Say Yes
            """)

    def test_error_num_args_not_match_num_params(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var P Q
            call What P Q
            proc What Is The Answer
                msg "42"
            end
            """)

    def test_error_recursive_call(self):
        self.assertRaises(
            Exception,
            Transpiler().transpile,
            """
            var A
            set a 20
            call Wrap a
            proc Say x
                msg "It is "x
                call Wrap X
            end
            Proc Wrap X
                call Say x
            eNd
            """)
