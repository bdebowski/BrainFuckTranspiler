# Brainfuck Interpreter
# Adapted from Sebastian Kaspari's code on github:
# https://github.com/pocmo/Python-Brainfuck
#
# Usage: ./brainfuck.py [FILE]

import sys
try:
    import getch
except ModuleNotFoundError:
    import bfinterpreter.getch as getch


def _execute(filename):
    f = open(filename, "r")
    evaluate(f.read())
    f.close()


def evaluate(code, instream=None, outstream=None):
    # Configure input reading and output writing
    read_char_fn = instream.read if instream else getch.getch
    read_char_args = (1,) if instream else ()
    write_char_fn = outstream.write if outstream else sys.stdout.write

    code = _cleanup(list(code))
    bracemap = _buildbracemap(code)

    cells, codeptr, cellptr, num_steps = [0], 0, 0, 0

    while codeptr < len(code):
        command = code[codeptr]

        if command == ">":
            cellptr += 1
            if cellptr == len(cells):
                cells.append(0)
        if command == "<":
            cellptr = 0 if cellptr <= 0 else cellptr - 1
        if command == "+":
            cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0
        if command == "-":
            cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255

        if command == "[" and cells[cellptr] == 0:
            codeptr = bracemap[codeptr]
        if command == "]" and cells[cellptr] != 0:
            codeptr = bracemap[codeptr]

        if command == ".":
            write_char_fn(chr(cells[cellptr]))
        if command == ",":
            cells[cellptr] = ord(read_char_fn(*read_char_args))

        codeptr += 1
        num_steps += 1

    return num_steps


def _cleanup(code):
    return ''.join(filter(lambda x: x in ['.', ',', '[', ']', '<', '>', '+', '-'], code))


def _buildbracemap(code):
    temp_bracestack, bracemap = [], {}

    for position, command in enumerate(code):
        if command == "[":
            temp_bracestack.append(position)
        if command == "]":
            start = temp_bracestack.pop()
            bracemap[start] = position
            bracemap[position] = start
    return bracemap


def main():
    if len(sys.argv) == 2:
        _execute(sys.argv[1])
    else:
        print("Usage:", sys.argv[0], "filename")


if __name__ == "__main__":
    main()
