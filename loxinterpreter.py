from typing import List, Dict, Union, Optional, Any

import loxExprAST
import loxStmtAST
import loxcallable
import loxclass
import loxenvironment
import loxglobals
import loxtoken
from loxerror import LoxRuntimeError, Return, raise_error


class Interpreter:
    tokentypes = loxtoken.TokenType

    def __init__(self):

        self.globals: loxenvironment.Environment = loxglobals.Globals().globals
        self.environment: loxenvironment.Environment = self.globals
        self.locals: Dict[loxExprAST.Expr, int] = dict()

    def interpret(self, stmts: List[loxStmtAST.Stmt]) -> None:
        try:
            for statement in stmts:
                self.execute(statement)
        except RuntimeError as error:
            print(error)

    def execute(self, stmt: loxStmtAST.Stmt) -> None:
        stmt.accept(self)

    def execute_list(self, stmt: List[loxStmtAST.Stmt]) -> None:
        for st in stmt:
            st.accept(self)

    def resolve(self, expr: loxExprAST.Expr, depth: int) -> None:
        self.locals[expr] = depth

    def execute_block(self, stmt: List[loxStmtAST.Stmt], environment: loxenvironment.Environment) -> None:
        previous_env: loxenvironment.Environment = self.environment
        try:
            self.environment = environment
            for statement in stmt:
                self.execute(statement)
        finally:
            self.environment = previous_env

    def visit_block_stmt(self, stmt: loxStmtAST.Block) -> None:
        self.execute_block(stmt.statements, loxenvironment.Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: loxStmtAST.Class) -> None:
        superclass: Optional[loxExprAST.Variable] = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, loxclass.LoxClass):
                raise_error(LoxRuntimeError, stmt.superclass.name, "Superclass must be a class.")
        self.environment.define(stmt.name.lexeme, None)
        if stmt.superclass is not None:
            self.environment = loxenvironment.Environment(self.environment)
            self.environment.define("super", superclass)
        methods: Dict[str, loxcallable.LoxFunction] = dict()
        for method in stmt.methods:
            function = loxcallable.LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        klass: loxclass.LoxClass = loxclass.LoxClass(stmt.name.lexeme, superclass, methods)
        if stmt.superclass is not None:
            self.environment = self.environment.enclosing
        self.environment.assign(stmt.name, klass)
        return None

    def visit_var_stmt(self, stmt: loxStmtAST.Var) -> None:
        value: Optional[loxExprAST.Expr] = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_while_stmt(self, stmt: loxStmtAST.While) -> None:
        while self.is_true(self.evaluate(stmt.condition)):
            # self.execute_list(stmt.body.statements)
            self.visit_block_stmt(stmt.body)
        return None

    def visit_assign_expr(self, expr: loxExprAST.Assign) -> loxExprAST.Expr:
        value: loxExprAST.Expr = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_print_stmt(self, stmt: loxStmtAST.Print) -> None:
        value: loxExprAST.Expr = self.evaluate(stmt.expression)
        print(value)
        return None

    def visit_return_stmt(self, stmt: loxStmtAST.Return) -> None:
        value: Optional[loxExprAST.Expr] = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visit_expression_stmt(self, stmt: loxStmtAST.Expression) -> None:
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt: loxStmtAST.Function) -> None:
        funct: loxcallable.LoxFunction = loxcallable.LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, funct)
        return None

    def visit_if_stmt(self, stmt: loxStmtAST.If) -> None:
        if self.is_true(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_variable_expr(self, expr) -> object:
        return self.lookup_variable(expr.name, expr)
        # return self.environment.get(expr.name)

    @staticmethod
    def visit_literal_expr(expr) -> Union[float, str, bool]:
        return expr.value

    def visit_logical_expr(self, expr) -> bool:
        left: bool = self.evaluate(expr.left)

        if expr.operator.type == Interpreter.tokentypes.OR:
            if self.is_true(left):
                return left
        elif not self.is_true(left):
            return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: loxExprAST.Set):
        set_object = self.evaluate(expr.set_object)
        if not isinstance(set_object, loxclass.LoxInstance):
            raise_error(LoxRuntimeError, expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        set_object.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: loxExprAST.Super):
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, "super")
        # "this" is always one level nearer than "super"'s environment.
        get_object = self.environment.get_at(distance - 1, "this")
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise_error(LoxRuntimeError, expr.method, "Undefined property '" + expr.method.lexeme + "'.")
        return method.bind(get_object)

    def visit_this_expr(self, expr: loxExprAST.This) -> object:
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr) -> Union[float, str, bool]:
        return self.evaluate(expr.expression)

    def visit_binary_expr(self, expr) -> Optional[Union[float, str, bool]]:
        left: Union[float, str, bool] = self.evaluate(expr.left)
        right: Union[float, str, bool] = self.evaluate(expr.right)

        if expr.operator.tok_type == Interpreter.tokentypes.MINUS:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) - float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.SLASH:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) / float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.STAR:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) * float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                raise_error(LoxRuntimeError, expr.operator, "Operands must both be a number or a string.")

        elif expr.operator.tok_type == Interpreter.tokentypes.GREATER:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) > float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.GREATER_EQUAL:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) >= float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.LESS:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) < float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.LESS_EQUAL:
            if self.check_number_operands(expr.operator, left, right):
                return float(left) <= float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.EQUAL_EQUAL:
            return self.is_equal(left, right)
        elif expr.operator.tok_type == Interpreter.tokentypes.BANG_EQUAL:
            return not self.is_equal(left, right)

        return None

    def visit_call_expr(self, expr: loxExprAST.Call) -> object:
        callee: loxcallable.LoxFunction = self.evaluate(expr.callee)
        arguments: List[object] = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))
        if not isinstance(callee, loxcallable.LoxCallable) and loxcallable.LoxCallable not in callee.__bases__:
            raise_error(LoxRuntimeError, expr.paren, "Can only call functions and classes.")

        # funct: loxcallable.LoxFunction = callee
        if len(arguments) != callee.arity():
            raise_error(LoxRuntimeError, expr.paren,
                        "Expected " + str(callee.arity()) + " arguments but got "
                        + str(len(arguments)) + ".")
        return callee.call(self, arguments)

    def visit_get_expr(self, expr: loxExprAST.Get):
        get_object = self.evaluate(expr.get_object)
        if isinstance(get_object, loxclass.LoxInstance):
            return get_object.get(expr.name)
        raise_error(LoxRuntimeError, expr.name, "Only instances have properties.")

    def visit_unary_expr(self, expr: loxExprAST.Unary) -> Union[float, bool, None]:
        right: loxExprAST.Expr = self.evaluate(expr.right)

        if expr.operator.tok_type == Interpreter.tokentypes.MINUS:
            if self.check_number_operands(expr.operator, right):
                assert isinstance(right, float)
                return float(right)
        elif expr.operator.tok_type == Interpreter.tokentypes.BANG:
            return self.is_true(right)
        return None

    def lookup_variable(self, name: loxtoken.Token, expr: loxExprAST.Expr) -> object:
        distance: int = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def evaluate(self, expr: loxExprAST.Expr) -> Any:
        return expr.accept(self)

    @staticmethod
    def is_true(expr: Any) -> bool:
        if expr is None:
            return False
        if isinstance(expr, bool):
            return expr
        return True

    @staticmethod
    def is_equal(o1: object, o2: object) -> bool:
        if o1 is None and o2 is None:
            return True
        if o1 is None:
            return False
        return o1 == o2

    @staticmethod
    def check_number_operands(operator: loxtoken.Token, op1: Any, op2: Any = None) -> bool:
        if op2 is None:
            if isinstance(op1, float):
                return True
            raise_error(LoxRuntimeError, operator, "Operand must be a number.")
        else:
            if isinstance(op1, float) and isinstance(op2, float):
                return True
            raise_error(LoxRuntimeError, operator, "Both operands must be a number.")
        return False
