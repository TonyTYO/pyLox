import enum
from typing import List, Dict, Iterator, TypeVar, Generic, Any

from loxerror import LoxError, raise_error
from loxtoken import Token
import loxExprAST
import loxStmtAST
import loxinterpreter

T = TypeVar('T')


# noinspection PyArgumentList
class Resolver:
    FunctionType = enum.Enum('FunctionType', 'NONE FUNCTION INITIALIZER METHOD')
    ClassType = enum.Enum('ClassType', 'NONE CLASS')

    def __init__(self, interpreter: loxinterpreter.Interpreter):

        self.interpreter = interpreter
        self.scopes: Stack[Dict[str, bool]] = Stack()
        self.current_function: Resolver.FunctionType = Resolver.FunctionType.NONE
        self.current_class: Resolver.ClassType = Resolver.ClassType.NONE

    def visit_block_stmt(self, stmt: loxStmtAST.Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visit_class_stmt(self, stmt: loxStmtAST.Class) -> None:
        enclosing_class = self.current_class
        self.current_class = Resolver.ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            raise_error(LoxError, stmt.superclass.name, "A class cannot inherit from itself.")
        if stmt.superclass is not None:
            self.resolve_expr(stmt.superclass)
        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes.peek()["super"] = True
        self.begin_scope()
        self.scopes.peek()["this"] = True
        for method in stmt.methods:
            if method.name.lexeme == "init":
                declaration: Resolver.FunctionType = Resolver.FunctionType.INITIALIZER
            else:
                declaration = Resolver.FunctionType.METHOD
            self.resolve_function(method, declaration)
        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class
        return None

    def visit_var_stmt(self, stmt: loxStmtAST.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)
        return None

    def visit_while_stmt(self, stmt: loxStmtAST.While) -> None:
        self.resolve_expr(stmt.condition)
        # self.resolve(stmt.body.statements)
        self.visit_block_stmt(stmt.body)
        return None

    def visit_function_stmt(self, stmt: loxStmtAST.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, Resolver.FunctionType.FUNCTION)
        return None

    def visit_if_stmt(self, stmt: loxStmtAST.If) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: loxStmtAST.Print) -> None:
        self.resolve_expr(stmt.expression)
        return None

    def visit_return_stmt(self, stmt: loxStmtAST.Return) -> None:
        if self.current_function == Resolver.FunctionType.NONE:
            raise_error(LoxError, stmt.keyword, "Cannot return from top-level code.")
        if stmt.value is not None:
            if self.current_function == Resolver.FunctionType.INITIALIZER:
                raise_error(LoxError, stmt.keyword, "Cannot return a value from an initializer.")
            self.resolve_expr(stmt.value)
        return None

    def visit_expression_stmt(self, stmt: loxStmtAST.Expression) -> None:
        self.resolve_expr(stmt.expression)
        return None

    def visit_variable_expr(self, expr: loxExprAST.Variable) -> None:
        if not self.scopes.is_empty() and self.scopes.peek().get(expr.name.lexeme) is False:
            raise_error(LoxError, expr.name, "Cannot read local variable in its own initializer.")
        self.resolve_local(expr, expr.name)
        return None

    def visit_assign_expr(self, expr: loxExprAST.Assign) -> None:
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_binary_expr(self, expr: loxExprAST.Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def visit_call_expr(self, expr: loxExprAST.Call) -> None:
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)
        return None

    def visit_get_expr(self, expr: loxExprAST.Get) -> None:
        self.resolve_expr(expr.get_object)
        return None

    def visit_super_expr(self, expr: loxExprAST.Super) -> None:
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_grouping_expr(self, expr: loxExprAST.Grouping) -> None:
        self.resolve_expr(expr.expression)
        return None

    # noinspection PyUnusedLocal
    @staticmethod
    def visit_literal_expr(expr: loxExprAST.Literal) -> None:
        return None

    def visit_logical_expr(self, expr: loxExprAST.Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def visit_set_expr(self, expr: loxExprAST.Set) -> None:
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.set_object)
        return None

    def visit_this_expr(self, expr: loxExprAST.This) -> None:
        if self.current_class == Resolver.ClassType.NONE:
            raise_error(LoxError, expr.keyword, "Cannot use 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_unary_expr(self, expr: loxExprAST.Unary) -> None:
        self.resolve_expr(expr.right)
        return None

    def resolve(self, stmts: List[loxStmtAST.Stmt]) -> None:
        try:
            for stmt in stmts:
                self.resolve_stmt(stmt)
        except LoxError as error:
            print(error)

    def resolve_stmt(self, stmt: loxStmtAST.Stmt) -> None:
        stmt.accept(self)

    def resolve_expr(self, expr: loxExprAST.Expr) -> None:
        expr.accept(self)

    def resolve_local(self, expr: loxExprAST.Expr, name: Token) -> None:
        pos = 0
        for scope in self.scopes:
            if name.lexeme in scope:
                self.interpreter.resolve(expr, pos)
                return
            pos += 1
        # Not found. Assume it is global.

    def resolve_function(self, funct: loxStmtAST.Function, functype: 'Resolver.FunctionType') -> None:
        enclosing_function: Resolver.FunctionType = self.current_function
        self.current_function = functype
        self.begin_scope()
        param: Token
        for param in funct.params:
            self.declare(param)
            self.define(param)
        self.resolve(funct.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.push(dict())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if self.scopes.is_empty():
            return None
        if name.lexeme in self.scopes.peek():
            raise_error(LoxError, name, "Variable with this name already declared in this scope.")
        self.scopes.peek()[name.lexeme] = False

    def define(self, name: Token):
        if self.scopes.is_empty():
            return None
        self.scopes.peek()[name.lexeme] = True


class Stack(Generic[T]):
    """ Class to implement a stack """

    def __init__(self, lst: List[T] = None) -> None:
        super(Stack, self).__init__()

        if lst is None:
            self.__stack: List[T] = []
        else:
            self.__stack = list(lst)

    def __iter__(self) -> Iterator[T]:
        return iter(reversed(self.__stack))

    def __str__(self) -> str:
        return str(self.__stack)

    def push(self, item: Any) -> None:
        """ Push item onto stack """
        self.__stack.append(item)

    def pop(self, index: int = -1) -> T:
        """ Pop item from stack """
        return self.__stack.pop(index)

    def peek(self) -> T:
        """ Peek top item in stack without removing """
        return self.__stack[-1]

    def get(self, no: int) -> T:
        """ Peek item at position no in stack """
        return self.__stack[-no]

    def empty(self) -> None:
        """ Clear out stack """
        self.__stack.clear()

    def size(self) -> int:
        """ Return no of items in stack """
        return len(self.__stack)

    def is_empty(self) -> bool:
        """ Return True if stack is empty """
        return not self.__stack
