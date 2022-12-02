from enum import Enum

# code block: condition, loop, proc_def, sequence
#   instr: var, set, add, sub, inc, dec, mul, divmod, div, mod, cmp, a2b, b2a, lset, lget, ifeq, ifneq, wneq, proc, call, end, read, msg
#   arg: varname, literal (string, char, number), [, ]
#   sep: whitespace
# comment
# white space

whitespace = {' ', '\t', '\n'}
digit = set(range(10))
var_prefix = set(['$', '_'] + list(map(chr, range(ord('a'), ord('z') + 1))) + list(map(chr, range(ord('A'), ord('Z') + 1))))
instr_prefix = set(list(map(chr, range(ord('a'), ord('z') + 1))) + list(map(chr, range(ord('A'), ord('Z') + 1))))
comment_prefix = {'#', '/', '-'}


class Section:
    def __init__(self, name, end: callable):
        self._end = end
        self.text = ""
        self.name = name

    def read(self, code: str) -> str:
        i = 0
        while i < len(code) and not self._end(code[i:]):
            self.text += code[i]
            i += 1
        return code[i:]


comment_section = Section("Comment", lambda x: x[0] == '\n')
whitespace_section = Section("WhiteSpace", lambda x: x[0] in instr_prefix or x[0] == '#' or x.startswith('//') or x.startswith('--'))
code_section = Section("Code", lambda x: x[0] == '#' or x.startswith('//') or x.startswith('--'))


def parse(code):
    sections = []
    section = comment_section
    while code:
        code = section.read(code)
        sections.append(section.text)
        section.text = ""
        if code.startswith('#') or code.startswith('//') or code.startswith('--'):
            section = comment_section
        elif code[:1] in whitespace:
            section = whitespace_section
        else:
            section = code_section
    return sections


"""
class Section(Enum):
    WHITE_SPACE = 1
    COMMENT = 2
    CODE_BLOCK = 3


class CodeSection(Enum):
    SEP = 1
    INSTR = 2
    ARG = 3


def parse(code: str):
    instructions = []
    section = Section.WHITE_SPACE
    code_section = None
    i = 0
    while i < len(code):
        c = code[i]

        if section == Section.WHITE_SPACE:
            if c in whitespace:
                i += 1
                continue
            if c == '#':
                section = Section.COMMENT
            elif c == '/':
                try:
                    if code[i+1] == '/':
                        section = Section.COMMENT
                    else:
                        raise RuntimeError("Invalid")
                except IndexError:
                    raise RuntimeError("Invalid")
            elif c == '-':
                try:
                    if code[i+1] == '-':
                        section = Section.COMMENT
                    else:
                        raise RuntimeError("Invalid")
                except IndexError:
                    raise RuntimeError("Invalid")
            elif c == 'r':
                try:
                    if code[i:i+3] == "rem" and code[i+3] in whitespace:
                        section = Section.COMMENT
                    elif code[i:i+4] == "read" and code[i+4] in whitespace:
                        section = Section.CODE_BLOCK
                        code_section = CodeSection.INSTR
                        instructions.append([c, []])
                    else:
                        raise RuntimeError("Invalid")
                except IndexError:
                    raise RuntimeError("Invalid")
            elif c in

        elif section == Section.COMMENT:
            pass

        else:   # CODE_BLOCK
            pass
        i += 1
"""
