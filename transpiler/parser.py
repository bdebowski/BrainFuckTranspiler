from enum import Enum

# code block: condition, loop, proc_def, sequence
#   instr: var, set, add, sub, inc, dec, mul, divmod, div, mod, cmp, a2b, b2a, lset, lget, ifeq, ifneq, wneq, proc, call, end, read, msg
#   arg: varname, literal (string, char, number)
# comment
# white space

class Section(Enum):
    WHITE_SPACE = 1
    COMMENT = 2
    CODE_BLOCK = 3

def parse(code: str):
    section = Section.WHITE_SPACE
    for i in range(len(code)):
        if section == Section.WHITE_SPACE:
            pass
        elif section == Section.COMMENT:
            pass
        else:   # CODE_BLOCK
            pass
