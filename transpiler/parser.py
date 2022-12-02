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


class Section(Enum):
    CODE = 1
    COMMENT = 2
    WHITE_SPACE = 3


def read(end: callable, code: str) -> (str, str):
    sec_text = ""
    i = 0
    while i < len(code) and not end(code[i:]):
        sec_text += code[i]
        i += 1
    return sec_text, code[i:]


comment_section_end = lambda x: x[0] == '\n'
whitespace_section_end = lambda x: x[0] in instr_prefix or x[0] == '#' or x.startswith('//') or x.startswith('--')
code_section_end = lambda x: x[0] == '#' or x.startswith('//') or x.startswith('--') or x[0] == '\n'


def parse(code):
    sections = []
    section_end = whitespace_section_end
    section = Section.WHITE_SPACE
    while code:
        sec_text, code = read(section_end, code)
        if section is Section.CODE:
            sections.append(sec_text)
        if code.startswith('#') or code.startswith('//') or code.startswith('--'):
            section_end = comment_section_end
            section = Section.COMMENT
        elif code[:1] in whitespace:
            section_end = whitespace_section_end
            section = Section.WHITE_SPACE
        else:
            section_end = code_section_end
            section = Section.CODE
    return sections

