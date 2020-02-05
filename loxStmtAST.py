from loxtoken import Token
from typing import List
from loxExprAST import Expr, Variable


class Stmt:

    def accept(self, visitor):
        pass


class Visitor:

    def visit_block_stmt(self, block_stmt: 'Block'): pass
    def visit_class_stmt(self, class_stmt: 'Class'): pass
    def visit_expression_stmt(self, expression_stmt: 'Expression'): pass
    def visit_function_stmt(self, function_stmt: 'Function'): pass
    def visit_if_stmt(self, if_stmt: 'If'): pass
    def visit_print_stmt(self, print_stmt: 'Print'): pass
    def visit_return_stmt(self, return_stmt: 'Return'): pass
    def visit_var_stmt(self, var_stmt: 'Var'): pass
    def visit_while_stmt(self, while_stmt: 'While'): pass


class Block(Stmt):

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: Visitor):
        return visitor.visit_block_stmt(self)


class Class(Stmt):

    def __init__(self, name: Token, superclass: Variable, methods: List['Function']):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor: Visitor):
        return visitor.visit_class_stmt(self)


class Expression(Stmt):

    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_expression_stmt(self)


class Function(Stmt):

    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: Visitor):
        return visitor.visit_function_stmt(self)


class If(Stmt):

    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: Visitor):
        return visitor.visit_if_stmt(self)


class Print(Stmt):

    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_print_stmt(self)


class Return(Stmt):

    def __init__(self, keyword: Token, value: Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_return_stmt(self)


class Var(Stmt):

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor):
        return visitor.visit_var_stmt(self)


class While(Stmt):

    def __init__(self, condition: Expr, body: Block):
        self.condition = condition
        self.body = body

    def accept(self, visitor: Visitor):
        return visitor.visit_while_stmt(self)
