from typing import List, Optional, Union, Any

import loxExprAST
import loxStmtAST
import loxtoken
from loxerror import LoxParseError, raise_error


class Parser:
    """ Parser class """

    tokentypes = loxtoken.TokenType

    def __init__(self):
        self.tokens: Optional[List[loxtoken.Token]] = None
        self.current: int = 0
        self.tokens: List[loxtoken.Token] = []

    # program → declaration* EOF ;
    def parse(self, tokens: List[loxtoken.Token], current: int) -> Optional[List[loxStmtAST.Stmt]]:
        """ Parse tokens starting at current
            Result returned in expressions 
            program → declaration* EOF ; """

        self.tokens = tokens
        self.current = current
        statements: List[loxStmtAST.Stmt] = []

        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    # ---------------------------------------------------------------------------------
    def declaration(self) -> Optional[loxStmtAST.Stmt]:
        """ declaration → classDecl | funDecl | varDecl | statement ; """

        try:
            if self.match(Parser.tokentypes.CLASS):
                return self.class_declaration()
            if self.match(Parser.tokentypes.FUN):
                return self.function("function")
            if self.match(Parser.tokentypes.VAR):
                return self.var_declaration()
            return self.statement()
        except LoxParseError as err:
            print(err)
            self.synchronize()
            return None

    def class_declaration(self):
        """ classDecl   → "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}" ; """

        name: loxtoken.Token = self.consume(Parser.tokentypes.IDENTIFIER, "Expect class name.")
        superclass: Optional[loxExprAST.Variable] = None
        if self.match(Parser.tokentypes.LESS):
            self.consume(Parser.tokentypes.IDENTIFIER, "Expect superclass name.")
            superclass = loxExprAST.Variable(self.previous())
        self.consume(Parser.tokentypes.LEFT_BRACE, "Expect '{' before class body.")
        methods: List[loxStmtAST.Function] = []
        while not self.check(Parser.tokentypes.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(Parser.tokentypes.RIGHT_BRACE, "Expect '}' after class body.")
        return loxStmtAST.Class(name, superclass, methods)

    def var_declaration(self) -> loxStmtAST.Var:
        """ varDecl → "var" IDENTIFIER ( "=" expression )? ";" ; """

        name: loxtoken.Token = self.consume(Parser.tokentypes.IDENTIFIER, "Expect variable name.")
        initializer: Optional[loxExprAST.Expr] = None
        if self.match(Parser.tokentypes.EQUAL):
            initializer = self.expression()
        self.consume(Parser.tokentypes.SEMICOLON, "Expect ';' after variable declaration.")
        return loxStmtAST.Var(name, initializer)

    def function(self, kind: str) -> loxStmtAST.Function:
        """ funDecl → "fun" function ; 
            function   → IDENTIFIER "(" parameters? ")" block ;
            parameters → IDENTIFIER ( "," IDENTIFIER )* ; """

        name: loxtoken.Token = self.consume(Parser.tokentypes.IDENTIFIER, f'Expect {kind} name.')
        self.consume(Parser.tokentypes.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: List[loxtoken.Token] = []
        if not self.check(Parser.tokentypes.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    raise_error(LoxParseError, self.peek(), "Cannot have more than 255 parameters.")
                parameters.append(self.consume(Parser.tokentypes.IDENTIFIER, "Expect parameter name."))
                if not self.match(Parser.tokentypes.COMMA):
                    break
        self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(Parser.tokentypes.LEFT_BRACE, f'Expect {{ before {kind} body.')  # {{ to escape { in string
        body: List[loxStmtAST.Stmt] = self.block_stmt()
        return loxStmtAST.Function(name, parameters, body)

    # ---------------------------------------------------------------------------------
    def statement(self) -> Any:
        """ statement → exprStmt | forStmt | ifStmt | printStmt | returnStmt | whileStmt | block ; """

        if self.match(Parser.tokentypes.LEFT_BRACE):
            return loxStmtAST.Block(self.block_stmt())
        if self.match(Parser.tokentypes.IF):
            return self.if_stmt()
        if self.match(Parser.tokentypes.PRINT):
            return self.print_stmt()
        if self.match(Parser.tokentypes.RETURN):
            return self.return_stmt()
        if self.match(Parser.tokentypes.WHILE):
            return self.while_stmt()
        if self.match(Parser.tokentypes.FOR):
            return self.for_stmt()
        return self.expression_stmt()

    def while_stmt(self) -> loxStmtAST.While:
        """ whileStmt → "while" "(" expression ")" statement ; """

        self.consume(Parser.tokentypes.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: loxExprAST.Expr = self.expression()
        self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after condition.")
        body: loxStmtAST.Block = self.statement()
        return loxStmtAST.While(condition, body)

    def for_stmt(self) -> loxStmtAST.Stmt:
        """ forStmt → "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement ; """

        self.consume(Parser.tokentypes.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(Parser.tokentypes.SEMICOLON):
            initializer: Optional[loxStmtAST.Stmt] = None
        elif self.match(Parser.tokentypes.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_stmt()
        condition: Optional[loxExprAST.Expr] = None
        if not self.check(Parser.tokentypes.SEMICOLON):
            condition = self.expression()
        self.consume(Parser.tokentypes.SEMICOLON, "Expect ';' after loop condition.")
        increment: Optional[loxExprAST.Expr] = None
        if not self.check(Parser.tokentypes.RIGHT_PAREN):
            increment = self.expression()
        self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Union[loxStmtAST.Block, loxStmtAST.While] = self.statement()
        if increment is not None:
            body = loxStmtAST.Block([body, loxStmtAST.Expression(increment)])
        if condition is None:
            condition = loxExprAST.Literal(True)
        body = loxStmtAST.While(condition, body)
        if initializer is not None:
            body = loxStmtAST.Block([initializer, body])
        return body

    def block_stmt(self) -> List[loxStmtAST.Stmt]:
        """ block → "{" declaration* "}" ; """

        statements: List[loxStmtAST.Stmt] = []
        while not self.check(Parser.tokentypes.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(Parser.tokentypes.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def if_stmt(self) -> loxStmtAST.If:
        """ ifStmt → "if" "(" expression ")" statement ( "else" statement )? ; """

        self.consume(Parser.tokentypes.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: loxExprAST.Expr = self.expression()
        self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch: loxStmtAST.Stmt = self.statement()
        else_branch: Optional[loxStmtAST.Stmt] = None
        if self.match(Parser.tokentypes.ELSE):
            else_branch = self.statement()

        return loxStmtAST.If(condition, then_branch, else_branch)

    def print_stmt(self) -> loxStmtAST.Print:
        """ printStmt → "print" expression ";" ; """

        value: loxExprAST.Expr = self.expression()
        self.consume(Parser.tokentypes.SEMICOLON, "Expect ';' after value.")
        return loxStmtAST.Print(value)

    def return_stmt(self) -> loxStmtAST.Return:
        """ returnStmt → "return" expression? ";" ; """

        keyword: loxtoken.Token = self.previous()
        value: Optional[loxExprAST.Expr] = None
        if not self.check(Parser.tokentypes.SEMICOLON):
            value = self.expression()
        self.consume(Parser.tokentypes.SEMICOLON, "Expect ';' after return value.")
        return loxStmtAST.Return(keyword, value)

    def expression_stmt(self) -> loxStmtAST.Expression:
        """ exprStmt → expression ";" ; """

        expr: loxExprAST.Expr = self.expression()
        self.consume(Parser.tokentypes.SEMICOLON, "Expect ';' after expression.")
        return loxStmtAST.Expression(expr)

    # ---------------------------------------------------------------------------------
    def expression(self) -> loxExprAST.Expr:
        """ Starting point for parsing expression 
            expression → assignment ; """

        return self.assignment()

    def assignment(self) -> loxExprAST.Expr:
        """ assignment → ( call "." )? IDENTIFIER "=" assignment | logic_or; """

        expr: loxExprAST.Expr = self.op_or()
        if self.match(Parser.tokentypes.EQUAL):
            equals: loxtoken.Token = self.previous()
            value: loxExprAST.Expr = self.assignment()
            if isinstance(expr, loxExprAST.Variable):
                name: loxtoken.Token = expr.name
                return loxExprAST.Assign(name, value)
            elif isinstance(expr, loxExprAST.Get):
                # get = expr
                return loxExprAST.Set(expr.get_object, expr.name, value)
            else:
                raise_error(LoxParseError, equals, "Invalid assignment target.")
        return expr

    def op_or(self) -> loxExprAST.Expr:
        """ logic_or → logic_and ( "or" logic_and )* ; """

        expr: loxExprAST.Expr = self.op_and()
        while self.match(Parser.tokentypes.OR):
            operator: loxtoken.Token = self.previous()
            right: loxExprAST.Expr = self.op_and()
            expr = loxExprAST.Logical(expr, operator, right)
        return expr

    def op_and(self) -> loxExprAST.Expr:
        """ logic_and → equality ( "and" equality )* ; """

        expr: loxExprAST.Expr = self.equality()
        while self.match(Parser.tokentypes.AND):
            operator: loxtoken.Token = self.previous()
            right: loxExprAST.Expr = self.equality()
            expr = loxExprAST.Logical(expr, operator, right)
        return expr

    def equality(self) -> loxExprAST.Expr:
        """ equality → comparison ( ( "!=" | "==" ) comparison )* """

        expr: loxExprAST.Expr = self.comparison()

        while self.match(Parser.tokentypes.BANG_EQUAL, Parser.tokentypes.EQUAL_EQUAL):
            operator: loxtoken.Token = self.previous()
            right_expr: loxExprAST.Expr = self.comparison()
            expr = loxExprAST.Binary(expr, operator, right_expr)

        return expr

    def comparison(self) -> loxExprAST.Expr:
        """ comparison → addition ( ( ">" | ">=" | "<" | "<=" ) addition )* """

        expr: loxExprAST.Expr = self.addition()

        while self.match(Parser.tokentypes.GREATER, Parser.tokentypes.GREATER_EQUAL, Parser.tokentypes.LESS,
                         Parser.tokentypes.LESS_EQUAL):
            operator: loxtoken.Token = self.previous()
            right_expr: loxExprAST.Expr = self.addition()
            expr = loxExprAST.Binary(expr, operator, right_expr)

        return expr

    def addition(self) -> loxExprAST.Expr:
        """ addition → multiplication ( ( "-" | "+" ) multiplication )* """

        expr: loxExprAST.Expr = self.multiplication()

        while self.match(Parser.tokentypes.MINUS, Parser.tokentypes.PLUS):
            operator: loxtoken.Token = self.previous()
            right_expr: loxExprAST.Expr = self.multiplication()
            expr = loxExprAST.Binary(expr, operator, right_expr)

        return expr

    def multiplication(self) -> loxExprAST.Expr:
        """ multiplication → unary ( ( "/" | "*" ) unary )* """

        expr: loxExprAST.Expr = self.unary()

        while self.match(Parser.tokentypes.SLASH, Parser.tokentypes.STAR):
            operator: loxtoken.Token = self.previous()
            right_expr: loxExprAST.Expr = self.unary()
            expr = loxExprAST.Binary(expr, operator, right_expr)

        return expr

    def unary(self) -> loxExprAST.Expr:
        """ unary → ( "!" | "-" ) unary | call """

        if self.match(Parser.tokentypes.BANG, Parser.tokentypes.MINUS):
            operator: loxtoken.Token = self.previous()
            right_expr: loxExprAST.Expr = self.unary()
            return loxExprAST.Unary(operator, right_expr)
        return self.call()

    def call(self) -> loxExprAST.Expr:
        """ call  → primary ( "(" arguments? ")" | "." IDENTIFIER )* ; """

        expr: loxExprAST.Expr = self.primary()
        while True:
            if self.match(Parser.tokentypes.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(Parser.tokentypes.DOT):
                name: loxtoken.Token = self.consume(Parser.tokentypes.IDENTIFIER, "Expect property name after '.'.")
                expr = loxExprAST.Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee) -> loxExprAST.Expr:
        """ arguments → expression ( "," expression )* """

        arguments: List[loxExprAST.Expr] = []
        if not self.check(Parser.tokentypes.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    raise_error(LoxParseError, self.peek(), "Cannot have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(Parser.tokentypes.COMMA):
                    break
        paren: loxtoken.Token = self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after arguments.")
        return loxExprAST.Call(callee, paren, arguments)

    # ---------------------------------------------------------------------------------
    def primary(self) -> Optional[loxExprAST.Expr]:
        """ primary    → "true" | "false" | "nil" | "this"
                         | NUMBER | STRING | IDENTIFIER | "(" expression ")"
                         | "super" "." IDENTIFIER ;

            NUMBER     → DIGIT+ ( "." DIGIT+ )? ;
            STRING     → '"' <any char except '"'>* '"' ;
            IDENTIFIER → ALPHA ( ALPHA | DIGIT )* ;
            ALPHA      → 'a' ... 'z' | 'A' ... 'Z' | '_' ;
            DIGIT      → '0' ... '9' ;"""

        if self.match(Parser.tokentypes.SUPER):
            keyword: loxtoken.Token = self.previous()
            self.consume(Parser.tokentypes.DOT, "Expect '.' after 'super'.")
            method: loxtoken.Token = self.consume(Parser.tokentypes.IDENTIFIER, "Expect superclass method name.")
            return loxExprAST.Super(keyword, method)
        if self.match(Parser.tokentypes.THIS):
            return loxExprAST.This(self.previous())
        if self.match(Parser.tokentypes.IDENTIFIER):
            return loxExprAST.Variable(self.previous())
        if self.match(Parser.tokentypes.FALSE):
            return loxExprAST.Literal(False)
        if self.match(Parser.tokentypes.TRUE):
            return loxExprAST.Literal(True)
        if self.match(Parser.tokentypes.NIL):
            return loxExprAST.Literal(None)

        if self.match(Parser.tokentypes.NUMBER, Parser.tokentypes.STRING):
            return loxExprAST.Literal(self.previous().literal)
        if self.match(Parser.tokentypes.LEFT_PAREN):
            expr: loxExprAST.Expr = self.expression()
            self.consume(Parser.tokentypes.RIGHT_PAREN, "Expect ')' after expression")
            return loxExprAST.Grouping(expr)

        raise_error(LoxParseError, self.peek(), "Expect expression.")
        return None

    # ---------------------------------------------------------------------------------
    def consume(self, tok_type: loxtoken.TokenType, message: str) -> Optional[loxtoken.Token]:
        """ If token of correct type advance otherwise raise error with message """
        if self.check(tok_type):
            return self.advance()
        raise_error(LoxParseError, self.peek(), message)
        return None

    def match(self, *tok_types: loxtoken.TokenType) -> bool:
        """ Check if current token matches types listed """
        for tok_type in tok_types:
            if self.check(tok_type):
                self.advance()
                return True
        return False

    def check(self, tok_type: loxtoken.TokenType) -> bool:
        """ Check if current token of type (type) """
        if self.is_at_end():
            return False
        return self.peek().tok_type == tok_type

    def advance(self) -> loxtoken.Token:
        """ Return token at current and advence current """
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """ Return True if at end of tokens """
        return self.peek().tok_type == Parser.tokentypes.EOF

    def peek(self) -> loxtoken.Token:
        """ Return current token without (re)moving """
        return self.tokens[self.current]

    def previous(self) -> loxtoken.Token:
        """ Return previous token """
        return self.tokens[self.current - 1]

    def synchronize(self):
        """ Synchronize for recovery after error """
        check_tokens = Parser.tokentypes.create_list(["class", "fun", "var", "for", "if", "while", "print", "return"])
        self.advance()
        while not self.is_at_end():
            if self.previous().tok_type == Parser.tokentypes.SEMICOLON:
                return
            if self.peek().tok_type in check_tokens:
                return
            self.advance()
