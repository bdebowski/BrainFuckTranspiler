import io
import re
from typing import Iterable, List


def tokenize(code: io.TextIOBase) -> Iterable[List[str]]:
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
