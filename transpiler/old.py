import re


class Var:
    def __init__(self, name, size=1):
        self.name = name
        self.size = size


class Translator:
    class VarBuilder():
        def __init__(self):
            self._re_var_name = re.compile(r"((?:_|$|[a-z])+(?:_|$|[a-z]|\d)*)(?:\s+|$)")
            self._re_list_decl = re.compile(r"((?:_|\$|[a-z])+(?:_|\$|[a-z]|\d)*)\s*\[\s*(\d+)\s*\](?:\s+|$)")

        def build(self, vars_str):
            vars = []
            while(vars_str.strip()):
                list_decl_match = self._re_list_decl.match(vars_str)
                if list_decl_match:
                    vars.append(Var(list_decl_match.group(1), list_decl_match.group(2)))
                    vars_str = vars_str[list_decl_match.end():]
                    continue
                var_decl_match = self._re_var_name.match(vars_str)
                if var_decl_match:
                    vars.append(Var(var_decl_match.group(1)))
                    vars_str = vars_str[var_decl_match.end():]
                    continue
                raise RuntimeError()
            return vars

    def __init__(self):
        self._generator = BrainfuckGenerator()
        self._instr_tbl = {
            "var": self._generator.declare_vars,
            "read": self._generator.read_input,
            "msg": self._generator.print_output,
            "set": self._generator.set_var,
            "inc": self._generator.inc_var,
            "dec": self._generator.dec_var,
            "add": self._generator.add,
            "sub": self._generator.sub,
            "mul": self._generator.mul,
            "divmod": self._generator.div_mod,
            "div": self._generator.div,
            "-mod": self._generator.mod
        }
        self._var_builder = self.VarBuilder()

    def translate(self, src_code):
        for line in src_code.split('\n'):
            instruction, params = self._interpret(line)
            instruction(params)

            # special 1:
            # if instruction is 'proc', enter procedure definition mode
            #   if already in procedure definition mode, raise
            # subsequent instructions will be added to procedure until 'end' encountered

            # special 2:
            # if instruction is 'ifeq', 'ifneq', 'wneq' enter block mode and set block depth = 1
            #   if already in block mode, increment block depth
            # add subsequent instructions to block at current block depth
            # if instruction is 'end' decrement block depth; if depth is 0 exit block mode

        return self._generator.get_program()

    def _interpret(self, line):
        # Strip comments
        code_str = line.split('//', 1)[0].split('--', 1)[0].split('#', 1)[0]
        instr_str, _, args_str = code_str.partition(" ")
        instr_str = instr_str.lower()

        # Handle empty or 'rem'
        if not instr_str or instr_str == "rem":
            return self._do_nil, []

        # Handle 'end'
        if instr_str == "end":
            return self._do_end, []

        # Handle variable names for 'var' instruction
        if instr_str == "var":
            params = self._var_builder.build(args_str.lower())
        # Handle variable names, string literals, and integer literals for all other instructions
        else:
            params = args_str.split()
            for i in range(len(params)):
                if not params[i].startswith("\"") and not params[i].startswith("\'"):
                    params[i] = params[i].lower()

        return self._instr_tbl[instr_str], params

    def _do_nil(self, _):
        pass

    def _do_end(self, _):
        pass


class BrainfuckGenerator:
    class Tape:
        def __init__(self):
            self._pos = 0

        def seek(self, pos):
            r = "" + '>' * (pos - self._pos) + '<' * (self._pos - pos)
            self._pos = pos
            return r

        def write(self, v, pos=None):
            r = ""
            if pos:
                r += self.seek(pos)
            r += "[-]" + "+" * v
            return r

    class VarTable:
        _MIN = 0
        _MAX = 1024

        def __init__(self):
            self._vars = {}  # {(name: (start, end), name: (start, end)}
            self._free = [(self._MIN, self._MAX)]  # [(start, end), (start, end)]

        def alloc(self, name, size):
            if name in self._vars:
                raise RuntimeError("Redeclaration of variable {}".format(name))
            for i, block in enumerate(self._free):
                if size <= block[1] - block[0]:
                    start, end = block[0], block[0] + size
                    self._vars[name] = (start, end)
                    self._free[i] = (end, self._free[i][1])
                    if self._free[i][0] == self._free[i][1]:
                        self._free.pop(i)
                    return
            raise RuntimeError("Out of memory declaring variable {}".format(name))

        def free(self, name):
            if name not in self._vars:
                raise RuntimeError("Variable {} does not exist".format(name))
            new_free = self._vars.pop(name)
            # Find last free block occuring before this new free block
            last = None
            next = self._free[0]
            i = 0
            while next and next[1] <= new_free[0]:
                i += 1
                last = next
                next = self._free[i] if i <= len(self._free) else None
            # insert the new free block and merge any adjacent blocks
            self._free.insert(i, new_free)
            if 0 < i and self._free[i - 1][1] == self._free[i][0]:
                self._free[i - 1][1] = (self._free[i - 1][0], self._free[i][1])
                self._free.pop(i)
                i -= 1
            if i < (len(self._free) - 1) and self._free[i][1] == self._free[i + 1][0]:
                self._free[i + 1] = (self._free[i][0], self._free[i + 1][1])
                self._free.pop(i)

        def pos(self, varname):
            return self._vars[varname][0]

    def __init__(self):
        self._program = ""
        self._tape = self.Tape()
        self._var_table = self.VarTable()
        self._var_table.alloc("__out__", 1)
        self._var_table.alloc("__t0__", 1)
        self._var_table.alloc("__t1__", 1)
        self._var_table.alloc("__t2__", 1)
        self._var_table.alloc("__t3__", 1)
        self._var_table.alloc("__t4__", 1)
        self._var_table.alloc("__t5__", 1)
        self._var_table.alloc("__t6__", 1)
        self._var_table.alloc("__t7__", 1)

    def get_program(self):
        return self._program

    def declare_vars(self, args):
        assert 0 < len(args)
        for var in args:
            self._var_table.alloc(var.name, var.size)

    def read_input(self, args):
        assert 1 == len(args)
        pos = self._var_table.pos(args[0])
        self._program += self._tape.seek(pos) + ","

    def print_output(self, args):
        for arg in args:
            if arg.startswith("\""):
                if not arg.endswith("\""):
                    raise RuntimeError()
                self._program += self._tape.seek(self._var_table.pos("__out__"))
                for c in arg[1:-1]:
                    self._program += self._tape.write(ord(c)) + "."
            else:
                self._program += self._tape.seek(self._var_table.pos(arg)) + "."

    def _zero_var(self, var):
        self._program += self._tape.write(0, self._var_table.pos(var))

    def _seek_to_var(self, var, inplace=False):
        code = self._tape.seek(self._var_table.pos(var))
        if inplace:
            self._program += code
        else:
            return code

    def _write_to_var(self, val, var, inplace=False):
        code = self._tape.write(val, self._var_table.pos(var))
        if inplace:
            self._program += code
        else:
            return code

    def set_var(self, args):
        assert 2 == len(args)
        a, b = args
        t0 = "__t0__"
        literal = self._get_literal(b)
        if literal:
            self._write_to_var(literal, a, inplace=True)
        else:
            """
            t0[-]
            a[-]
            b[a+t0+b-]
            t0[b+t0-]
            """
            self._zero_var(t0)
            self._zero_var(a)
            self._program += self._seek_to_var(b) + "[" + self._seek_to_var(a) + "+" + self._seek_to_var(t0) + "+" + self._seek_to_var(b) + "-" + "]"
            self._program += self._seek_to_var(t0) + "[" + self._seek_to_var(b) + "+" + self._seek_to_var(t0) + "-" + "]"

    def inc_var(self, args):
        self._delta_var(args)

    def dec_var(self, args):
        self._delta_var(args, sign="-")

    def _delta_var(self, args, sign="+"):
        assert 2 == len(args)
        a, b = args
        t0 = "__t0__"
        not_sign = "-" if sign == "+" else "+"
        literal = self._get_literal(b)
        if literal:
            self._program += self._seek_to_var(a) + sign * literal + not_sign * -literal
        else:
            """
            t0[-]
            b[a(sign)t0+b-]
            t0[b+t0-]
            """
            self._zero_var(t0)
            self._program += self._seek_to_var(b) + "[" + self._seek_to_var(a) + sign + self._seek_to_var(t0) + "+" + self._seek_to_var(b) + "-" + "]"
            self._program += self._seek_to_var(t0) + "[" + self._seek_to_var(b) + "+" + self._seek_to_var(t0) + "-" + "]"

    def add(self, args):
        assert 3 == len(args)
        a, b, c = args
        t1 = "__t1__"
        self._zero_var(t1)
        self.inc_var([t1, a])
        self.inc_var([t1, b])
        self._zero_var(c)
        self.inc_var([c, t1])

    def sub(self, args):
        assert 3 == len(args)
        a, b, c = args
        t1 = "__t1__"
        self._zero_var(t1)
        self.inc_var([t1, a])
        self.dec_var([t1, b])
        self._zero_var(c)
        self.inc_var([c, t1])

    def mul(self, args):
        assert 3 == len(args)
        a, b, c = args
        t1 = "__t1__"
        """
        c[-]
        t1[-]
        a[t1+a-]
        t1[
          _inc(c, b)_
          a+t1-]
        """
        self._zero_var(c)
        self._zero_var(t1)
        self._program += self._seek_to_var(a) + "[" + self._seek_to_var(t1) + "+" + self._seek_to_var(a) + "-]"
        self._program += self._seek_to_var(t1) + "["
        self.inc_var([c, b])
        self._program += self._seek_to_var(a) + "+" + self._seek_to_var(t1) + "-]"

    def div_mod(self, args):
        assert 4 == len(args)
        a, b, c, d = args
        zero, q, r, ddend, dsor, end = "__t2__", "__t3__", "__t4__", "__t5__", "__t6__", "__t7__"
        """
        _set_var(z, 0)_
        _set_var(ddend, a)_
        _set_var(dsor, b)_
        _set_var(q, 0)_
        ddend[
          _set_var(r, ddend)_
          _set_var(end, 1)_
          z[dsor-[end[-]]ddend-[end[-]]end]
          dsor[r[-]]
          r[q+z]
          ddend
        ]
        _set_var(c, q)_
        _set_var(d, r)_
        """
        self._zero_var(zero)
        self._zero_var(q)
        self.set_var([ddend, a])
        self.set_var([dsor, b])
        self._program += self._seek_to_var(ddend) + "["
        self.set_var([r, ddend])
        self.set_var([end, "1"])
        self._program += self._seek_to_var(zero) + "[" + self._seek_to_var(dsor) + "-[" + self._seek_to_var(end) + "[-]]" + self._seek_to_var(ddend) + "-[" + self._seek_to_var(end) + "[-]]" + self._seek_to_var(end) + "]"
        self._program += self._seek_to_var(dsor) + "[" + self._seek_to_var(r) + "[-]]"
        self._program += self._seek_to_var(r) + "[" + self._seek_to_var(q) + "+" + self._seek_to_var(zero) + "]"
        self._program += self._seek_to_var(ddend) + "]"
        self.set_var([c, q])
        self.set_var([d, r])

    def div(self, args):
        assert 3 == len(args)
        a, b, c = args
        self.div_mod([a, b, c, "__t1__"])

    def mod(self, args):
        assert 3 == len(args)
        a, b, c = args
        self.div_mod([a, b, "__t1__", c])

    @staticmethod
    def _get_literal(arg):
        literal = None
        if arg.startswith("'"):
            literal = ord(arg[1:-1])
        else:
            try:
                literal = int(arg)
            except ValueError:
                pass
        if literal:
            literal &= 0xff
        return literal
