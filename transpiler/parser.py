import io
import re
from typing import List, Generator, Iterator, Dict
from dataclasses import dataclass, field


def tokenize(code: io.TextIOBase) -> Generator[List[str], None, None]:
    """
    Reads the code as an io stream line by line.
    Skips/Ignores comments and whitespaces.
    Returns an iterable of [instr, arg0, arg1, ...] lists.
    Detects various syntax errors and raises RuntimeError on each.
    """
    
    instruction_words = ("var", "set", "add", "sub", "inc", "dec", "mul", "divmod", "div", "mod", "cmp", "a2b", "b2a", "lset", "lget", "ifeq", "ifneq", "wneq", "proc", "call", "end", "read", "msg")
    instr_words_pattern = '|'.join(instruction_words)
    char_element_pattern = r"[^\'\"\\]|\\\\|\\\'|\\\"|\\n|\\r|\\t"
    char_pattern = fr"\'({char_element_pattern})\'"
    str_pattern = fr"\"({char_element_pattern})*\""
    var_name_pattern = r"[$_a-zA-Z][$_a-zA-Z\d]*"
    
    for line_num, line in enumerate(code, start=1):
        # Detect and skip empty lines and 'rem' comment lines
        line = line.lstrip()
        if not line or re.match(r"rem\s", line, flags=re.IGNORECASE):
            continue

        # Extract the instruction
        m = re.match(fr"({instr_words_pattern})(\s|--|#|//|$)", line, flags=re.IGNORECASE)
        if not m:
            raise RuntimeError("Line {}: Invalid instruction or syntax \'{}\'".format(line_num, line))
        instr = m.group(1).lower()
        instr_and_args = [instr]
        line = line[len(instr):].lstrip()

        # Extract instruction args
        while line and not re.match(r"#|//|--", line):
            # Extract string
            m = re.match(fr"({str_pattern})(\s|--|#|//|{var_name_pattern}|$)", line)
            if m:
                arg = m.group(1)
                instr_and_args.append(arg)
                line = line[len(arg):].lstrip()
                continue
            # Extract char
            m = re.match(fr"({char_pattern})(\s|--|#|//|$)", line)
            if m:
                arg = m.group(1)
                instr_and_args.append(arg)
                line = line[len(arg):].lstrip()
                continue
            # Extract number
            m = re.match(r"(-?\d+)(\s|--|#|//|$)", line)
            if m:
                arg = m.group(1)
                instr_and_args.append(arg)
                line = line[len(arg):].lstrip()
                continue
            # Extract variable
            m = re.match(fr"({var_name_pattern}(\s*\[\s*\d+\s*])?)(\s|--|#|//|{str_pattern}|$)", line)
            if m:
                arg = m.group(1).lower()
                instr_and_args.append(arg)
                line = line[len(arg):].lstrip()
                continue
            # No matches above therefore error
            raise RuntimeError("Line {}: Invalid args or syntax \'{}\'".format(line_num, line))
        yield instr_and_args


@dataclass
class Node:
    instr: str
    args: List[str]
    parent: 'Node' = None
    children: List['Node'] = field(default_factory=list)


class VarTable:
    def __init__(self, start_index=0):
        self._ctr = start_index
        self.vars = dict()

    def add(self, varname, size=1):
        self.vars[varname] = self._ctr
        self._ctr += size

    def add_from_args(self, instr_args: List[str]):
        for arg in instr_args:
            if '[' in arg:
                varname = re.match(r"[$_a-zA-Z][$_a-zA-Z\d]*", arg).group(0)
                size = int(re.match(r".+\s*\[\s*(\d+)", arg).group(1))
                self.add(varname, size=size)
            else:
                self.add(arg)


@dataclass
class Procedure:
    name: str
    args: List[str]
    ast: Node


def parse(instrs_and_args: Iterator[List[str]], root=None, var_table: VarTable = None, proc_table: Dict[str, Procedure] = None) -> Node:
    """
    Parses the token stream of instructions and their args into an Abstract Syntax Tree.
    Variables are added to the provided VarTable (and not to the AST).
    Procedure definitions are added to the provided proc_table, with each procedure being parsed as an AST.
    Returns the root of the AST.
    """
    if not root:
        root = Node("", [])

    parent = root
    for instr_and_args in instrs_and_args:
        instr = instr_and_args[0]
        args = instr_and_args[1:]

        if instr == "end":
            if parent.instr == "proc":
                return root
            parent = parent.parent
            continue

        if instr == 'proc':
            proc_table[args[0]] = Procedure(args[0], args[1:], parse(instrs_and_args, root=Node("proc", [])))
            continue

        if instr == 'var':
            var_table.add_from_args(args)
            continue

        node = Node(instr, args, parent=parent)
        parent.children.append(node)
        if instr == "ifeq" or instr == "ifneq" or instr == "wneq":
            parent = node
    return root


def inline(ast: Node, proc_table: Dict[str, Procedure], replace_vars: Dict[str, str] = None):
    """
    Replaces all 'call <proc_name> <args>*' instances in the AST with the corresponding procedure's AST.
    """
    if replace_vars:
        for i in range(len(ast.args)):
            arg = ast.args[i]
            if arg in replace_vars:
                ast.args[i] = replace_vars[arg]
    if ast.instr == 'call':
        proc = proc_table[ast.args[0]]
        for child in proc.ast.children:
            ast.children.append(child)
            child.parent = ast
            inline(child, proc_table, replace_vars={key: val for key, val in zip(proc.args, ast.args[1:])})
        return
    for child in ast.children:
        inline(child, proc_table, replace_vars=replace_vars)
    return
