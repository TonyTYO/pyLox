""" Utility to generate ExprAST module
    and StmtAST module"""

import sys


class GenerateAST:
    """ Class to generate ExprAST module
        and StmtAST module

        _types variables contain list of types
        with parameters (type and name) """

    expr_types = ["Assign   : Token name, Expr value",
                  "Binary   : Expr left, Token operator, Expr right",
                  "Call     : Expr callee, Token paren, List[Expr] arguments",
                  "Get      : Expr get_object, Token name",
                  "Grouping : Expr expression",
                  "Literal  : object value",
                  "Logical  : Expr left, Token operator, Expr right",
                  "Set      : Expr set_object, Token name, Expr value",
                  "Super    : Token keyword, Token method",
                  "This     : Token keyword",
                  "Unary    : Token operator, Expr right",
                  "Variable : Token name"]

    stmt_types = ["Block        : List[Stmt] statements",
                  "Class        : Token name, Variable superclass, List['Function'] methods",
                  "Expression   : Expr expression",
                  "Function     : Token name, List[Token] params, List[Stmt] body",
                  "If           : Expr condition, Stmt then_branch, Stmt else_branch",
                  "Print        : Expr expression",
                  "Return       : Token keyword, Expr value",
                  "Var          : Token name, Expr initializer",
                  "While        : Expr condition, Block body"]

    def __init__(self, output_dir):
        self.output_dir = output_dir
        if self.output_dir and self.output_dir[-1] != ".":
            self.output_dir += "."
        self.file_ref = None
        self.types = None

    def define_ast(self, name):
        """ Main generating function
            name: Expr or Stmt """
        print("Generating : " + "lox" + name + "AST.py")
        with open(self.output_dir + "lox" + name + "AST.py", "w") as mod:
            self.types = getattr(GenerateAST, name.lower() + "_types")
            self.define_header(mod, name)
            self.define_class(mod, name)
            self.write_newline(mod)
            self.define_visitor(mod, name)
            self.get_classes(mod, name)

    def define_header(self, file_ref, name):
        """ Write headers to file """
        self.write_ln(file_ref, "from loxtoken import Token\n")
        self.write_ln(file_ref, "from typing import List\n")
        if name == "Stmt":
            self.write_ln(file_ref, "from loxExprAST import Expr, Variable\n")
        self.write_newline(file_ref)
        self.write_newline(file_ref)

    def define_class(self, file_ref, name):
        """ Write base class to file """
        self.write_ln(file_ref, "class " + name + ":\n")
        self.write_newline(file_ref)
        self.write_ln(file_ref, "def accept(self, visitor):\n", indent=4)
        self.write_ln(file_ref, "pass\n", indent=8)
        self.write_newline(file_ref)

    def define_visitor(self, file_ref, baseclass):
        """ Write Visitor class to file """
        self.write_ln(file_ref, "class Visitor:\n")
        self.write_newline(file_ref)
        for entry in self.types:
            details = entry.split(":")
            classname = details[0].strip()
            self.write_ln(file_ref,
                          "def visit_" + classname.lower() + "_" + baseclass.lower() + "(self, " + classname.lower() +
                          "_" + baseclass.lower() + ": '" + classname + "'): pass\n",
                          indent=4)

    def get_classes(self, file_ref, baseclass):
        """ Write individual classes to file
            baseclass: Expr or Stmt """
        for entry in self.types:
            details = entry.split(":")
            classname = details[0].strip()
            fieldnames = details[1].split(", ")
            self.write_newline(file_ref)
            self.write_newline(file_ref)
            self.write_ln(file_ref, "class " + classname + "(" + baseclass + "):\n")
            self.write_newline(file_ref)
            init_line = "def __init__(self"
            assign_lines = []
            for field in fieldnames:
                args = field.split()
                entry = args[0].strip()
                name = args[1].strip()
                init_line = init_line + ", " + name + ": " + entry
                ass_line = "self." + name + " = " + name
                assign_lines.append(ass_line)
            init_line = init_line + "):\n"
            self.write_ln(file_ref, init_line, indent=4)
            for line in assign_lines:
                self.write_ln(file_ref, line + "\n", indent=8)
            self.write_newline(file_ref)
            self.write_ln(file_ref, "def accept(self, visitor: Visitor):\n", indent=4)
            self.write_ln(file_ref,
                          "return visitor.visit_" + classname.lower() + "_" + baseclass.lower() + "(self)\n", indent=8)

    @staticmethod
    def write_ln(file_ref, text, indent=0, char=""):
        """ Write formatted text to file """
        file_ref.write("{1:>{0}}{2}".format(indent, char, text))

    @staticmethod
    def write_newline(file_ref):
        """ Write new line to file """
        file_ref.write("\n")


def main():
    """ Main function
        Get arguments and run """

    try:
        args = list(sys.argv)
        if len(args) > 2:
            print("Usage: generate_ast <output directory> default current")
        else:
            if len(args) == 2:
                generator = GenerateAST(args[1])
            else:
                generator = GenerateAST("")
            generator.define_ast("Expr")
            generator.define_ast("Stmt")
    except SystemExit as e:
        print("System Exit: ", e.code)


if __name__ == '__main__':
    main()
