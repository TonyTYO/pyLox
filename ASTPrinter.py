from typing import List, Union

import loxExprAST
import loxStmtAST
import loxtoken


class ASTStmtPrinter(loxStmtAST.Visitor):

    INDENT: int = 0     # Indent for statement blocks

    def print(self, stmt: Union[loxStmtAST.Stmt, List[loxStmtAST.Stmt]]) -> str:
        """ Print statement or list of statements """
        if isinstance(stmt, list):
            return self.print_list(stmt)
        else:
            if stmt is not None:
                return stmt.accept(self)
        return ""

    @staticmethod
    def print_list(stmt: List[loxStmtAST.Stmt]) -> str:
        """ Print list of statements with indent """
        print_st: str = "\n" + ASTStmtPrinter.INDENT * ' ' + "Start List ===\n"
        if ASTStmtPrinter.INDENT != 0:
            ASTStmtPrinter.INDENT = int(ASTStmtPrinter.INDENT * 2)
        else:
            ASTStmtPrinter.INDENT = 4
        if stmt:
            for st in stmt:
                print_st += ASTStmtPrinter.INDENT * ' ' + ASTStmtPrinter().print(st) + "\n"
            if ASTStmtPrinter.INDENT != 4:
                ASTStmtPrinter.INDENT = int(ASTStmtPrinter.INDENT / 2)
            else:
                ASTStmtPrinter.INDENT = 0
            return print_st + ASTStmtPrinter.INDENT * ' ' + "End List ===\n"
        return ""

    def visit_block_stmt(self, stmt: loxStmtAST.Block) -> str:
        return "\n" + stmt.__class__.__name__ + ASTStmtPrinter().print(stmt.statements)

    def visit_class_stmt(self, stmt: loxStmtAST.Class) -> str:
        super_class: str = ""
        if stmt.superclass is not None:
            super_class = " < " + ASTPrinter().print(stmt.superclass)
        str_method: str = ""
        for method in stmt.methods:
            str_method += self.visit_function_stmt(method)
        return "\n" + stmt.__class__.__name__ + " " + stmt.name.lexeme + super_class + "\n" + str_method

    def visit_var_stmt(self, stmt: loxStmtAST.Var) -> str:
        return stmt.__class__.__name__ + " " + stmt.name.lexeme + " " + ASTPrinter().print(stmt.initializer)

    def visit_expression_stmt(self, stmt: loxStmtAST.Expression) -> str:
        return stmt.__class__.__name__ + " " + ASTPrinter().print(stmt.expression)

    def visit_function_stmt(self, stmt: loxStmtAST.Function) -> str:
        parameters: str = ""
        for par in stmt.params:
            parameters = parameters + par.lexeme + " "
        return stmt.__class__.__name__ + " " + stmt.name.lexeme + " " + parameters + " " + ASTStmtPrinter().print(
            stmt.body)

    def visit_if_stmt(self, stmt: loxStmtAST.If) -> str:
        return stmt.__class__.__name__ + " " + ASTPrinter().print(stmt.condition) + ASTStmtPrinter().print(
            stmt.then_branch) + ASTStmtPrinter().print(stmt.else_branch)

    def visit_while_stmt(self, stmt: loxStmtAST.While) -> str:
        return stmt.__class__.__name__ + " " + ASTPrinter().print(stmt.condition) + self.visit_block_stmt(
            stmt.body)  # + ASTStmtPrinter().print(stmt.body.statements)

    def visit_print_stmt(self, stmt: loxStmtAST.Print) -> str:
        return stmt.__class__.__name__ + " " + ASTPrinter().print(stmt.expression)

    def visit_return_stmt(self, stmt: loxStmtAST.Return) -> str:
        return stmt.__class__.__name__ + " " + stmt.keyword.lexeme + " " + ASTPrinter().print(stmt.value)


class ASTPrinter(loxExprAST.Visitor):

    def print(self, expr: Union[loxExprAST.Expr, List[loxExprAST.Expr]]) -> str:
        """ Print expression """
        print_exp: str = ""
        if isinstance(expr, list):
            for ex in expr:
                print_exp += ASTPrinter().print(ex) + " "
            return print_exp
        return expr.accept(self)

    def visit_call_expr(self, expr: loxExprAST.Call) -> str:
        return self.parenthesize(
            ASTPrinter().print(expr.callee) + " :" + expr.paren.to_line() + " :" + ASTPrinter().print(expr.arguments))

    def visit_assign_expr(self, expr: loxExprAST.Assign) -> str:
        return self.parenthesize("assign " + expr.name.lexeme, expr.value)

    def visit_variable_expr(self, expr: loxExprAST.Variable) -> str:
        return expr.name.lexeme

    def visit_get_expr(self, expr: loxExprAST.Get) -> str:
        return self.parenthesize("get " + ASTPrinter().print(expr.get_object) + "." + expr.name.lexeme)

    def visit_set_expr(self, expr: loxExprAST.Set) -> str:
        return self.parenthesize("set " + ASTPrinter().print(expr.set_object) + "." + expr.name.lexeme,
                                 expr.value)  # ASTPrinter().print(expr.object) + "." +

    def visit_this_expr(self, expr: loxExprAST.This) -> str:
        return expr.__class__.__name__ + " " + expr.keyword.lexeme

    def visit_super_expr(self, expr: loxExprAST.Super) -> str:
        return self.parenthesize("super " + expr.method.lexeme)

    def visit_logical_expr(self, expr: loxExprAST.Logical) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_binary_expr(self, expr: loxExprAST.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: loxExprAST.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: loxExprAST.Literal) -> str:
        if expr.value is None:
            return "None"
        return str(expr.value)

    def visit_unary_expr(self, expr: loxExprAST.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs: loxExprAST.Expr) -> str:
        """ Parenthesize expression """
        builder: list = list()
        builder.append("(")
        builder.append(name)

        for exp in exprs:
            builder.append(" ")
            builder.append(exp.accept(self))
        builder.append(")")
        return "".join(builder)


def main():
    """ Print test expression """
    expression = loxExprAST.Binary(
        loxExprAST.Unary(
            loxtoken.Token(loxtoken.TokenType.MINUS, "-", None, 1),
            loxExprAST.Literal(123)),
        loxtoken.Token(loxtoken.TokenType.STAR, "*", None, 1),
        loxExprAST.Grouping(
            loxExprAST.Literal(45.67)))

    print(ASTPrinter().print(expression))


if __name__ == '__main__':
    main()
