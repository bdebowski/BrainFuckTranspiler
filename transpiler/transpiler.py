from io import StringIO

from transpiler.parser import *


def print_ast(ast: Node):
    #print("{} {}".format(ast.instr, ' '.join(ast.args)))
    #for child in ast.children:
    #    print_ast(child)
    print(create_intermediate_bf(ast))


def create_intermediate_bf(ast: Node, var_table: VarTable) -> [str]:
    def visit(code: [str], node: Node, var_table):
        new_code = []
        for child in node.children:
            new_code += visit(code, child, var_table)
        return codify(new_code, node, var_table)

    def codify(code: [str], node: Node, var_table: VarTable):
        if node.instr == "call" or node.instr == '':
            return code
        if node.instr == "ifeq" or node.instr == "ifneq" or node.instr == "wneq":
            return [node.instr, *node.args, '['] + code + [']']
        return code + [node.instr, *node.args]

    return visit([], ast)


def transpile(code: str) -> str:
    var_table = VarTable()
    proc_table = {}
    ast = parse(tokenize(StringIO(code)), var_table=var_table, proc_table=proc_table)
    inline(ast, proc_table)

    print("Var Table:")
    for k, v in var_table.vars.items():
        print("{} {}".format(k, v))
    print()

    print_ast(ast)

