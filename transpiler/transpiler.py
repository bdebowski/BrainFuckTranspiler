from transpiler.old import Translator


def transpile(code):
    return Translator().translate(code)


def clean_and_normalize(code: str) -> str:
    """
    - Remove comments
    - Remove white space except for single space between tokens
    - Convert to lowercase (except string contents)
    """
    def remove_inline_comment_and_lower_case(code_line):
        in_str = False
        lower_cased = ""
        partial_line = ""
        for i in range(len(code_line)):
            partial_line += code_line[i]

            if code_line[i] == '"':
                in_str = not in_str
                if in_str:
                    partial_line = partial_line.lower()
                lower_cased += partial_line
                partial_line = ""

            if not in_str:
                if code_line[i] == '/' and code_line[i-1] == '/':
                    return lower_cased + partial_line[:-2].lower()
                if code_line[i] == '-' and code_line[i-1] == '-':
                    return lower_cased + partial_line[:-2].lower()
                if code_line[i] == '#':
                    return lower_cased + partial_line[:-1].lower()

        return lower_cased + partial_line.lower()

    tokens = []
    for line in code.split('\n'):
        # Remove whole line comments
        if line.lstrip().lower().startswith("rem"):
            continue
        # Remove inline comments (if any), convert to lowercase, remove leading and trailing white space, and split into tokens
        tokens += remove_inline_comment_and_lower_case(line).strip().split()

    return ' '.join(tokens)
