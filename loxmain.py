from typing import List, TYPE_CHECKING
import sys

import ASTPrinter
import loxerror
import loxinterpreter
import loxparser
import loxresolver
import loxscanner

if TYPE_CHECKING:
    import loxtoken
    import loxStmtAST


class Lox:
    """ Main program class
        Runs the Lox interpreter """

    had_error: bool = False  # flag error to stop processing

    def __init__(self, args: List[str]) -> None:

        self.scanner = loxscanner.Scanner()
        self.parser = loxparser.Parser()
        self.interpreter = loxinterpreter.Interpreter()
        self.resolver = loxresolver.Resolver(self.interpreter)
        self.line_no: int = 0

        if len(args) > 1:
            print("Usage: pyLox [script]")
            sys.exit(1)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, file_name: str):
        """ Run script from file
            Read whole file into string """

        with open(file_name, 'r') as source_file:
            self.run(source_file.read())

    def run_prompt(self):
        """ Run interactively from prompt """

        while True:
            line: str = input(">>")
            if line.lower() == "quit":
                break
            self.run(line)
            loxerror.had_error = False

    def run(self, source: str):
        """ Run interpreter """

        tokens: List[loxtoken.Token] = self.scanner.scan_tokens(source)
        statements: List[loxStmtAST.Stmt] = self.parser.parse(tokens, 0)
        if loxerror.had_error:
            return
        if statements:
            self.resolver.resolve(statements)
            print("ASTPrinter output ----------")
            for stmt in statements:
                print(ASTPrinter.ASTStmtPrinter().print(stmt))
            print("ASTPrinter end -------------")
            print()
            print("Resolver output ------------")
            for key in self.interpreter.locals:
                print(ASTPrinter.ASTPrinter().print(key), self.interpreter.locals[key])
            print("Resolver end ---------------")
            print()

            self.interpreter.interpret(statements)
