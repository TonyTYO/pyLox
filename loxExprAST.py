from loxtoken import Token
from typing import List


class Expr:

    def accept(self, visitor):
        pass


class Visitor:

    def visit_assign_expr(self, assign_expr: 'Assign'): pass
    def visit_binary_expr(self, binary_expr: 'Binary'): pass
    def visit_call_expr(self, call_expr: 'Call'): pass
    def visit_get_expr(self, get_expr: 'Get'): pass
    def visit_grouping_expr(self, grouping_expr: 'Grouping'): pass
    def visit_literal_expr(self, literal_expr: 'Literal'): pass
    def visit_logical_expr(self, logical_expr: 'Logical'): pass
    def visit_set_expr(self, set_expr: 'Set'): pass
    def visit_super_expr(self, super_expr: 'Super'): pass
    def visit_this_expr(self, this_expr: 'This'): pass
    def visit_unary_expr(self, unary_expr: 'Unary'): pass
    def visit_variable_expr(self, variable_expr: 'Variable'): pass


class Assign(Expr):

    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_assign_expr(self)


class Binary(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_expr(self)


class Call(Expr):

    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: Visitor):
        return visitor.visit_call_expr(self)


class Get(Expr):

    def __init__(self, get_object: Expr, name: Token):
        self.get_object = get_object
        self.name = name

    def accept(self, visitor: Visitor):
        return visitor.visit_get_expr(self)


class Grouping(Expr):

    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):

    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_literal_expr(self)


class Logical(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visit_logical_expr(self)


class Set(Expr):

    def __init__(self, set_object: Expr, name: Token, value: Expr):
        self.set_object = set_object
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_set_expr(self)


class Super(Expr):

    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor: Visitor):
        return visitor.visit_super_expr(self)


class This(Expr):

    def __init__(self, keyword: Token):
        self.keyword = keyword

    def accept(self, visitor: Visitor):
        return visitor.visit_this_expr(self)


class Unary(Expr):

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_expr(self)


class Variable(Expr):

    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: Visitor):
        return visitor.visit_variable_expr(self)
