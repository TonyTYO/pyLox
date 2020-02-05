from typing import Union, Type

import loxtoken

had_error: bool = False  # flag error to stop processing
had_runtime_error: bool = False  # flag error to stop processing


def raise_error(cls: Union[Type['LoxError'], Type['LoxParseError'],
                           Type['LoxRuntimeError']], token: Union[loxtoken.Token, int], msg: str) \
        -> None:
    """ General function to raise an error
        using the relevant error class given in cls"""
    err_msg: str = cls(token, msg).report()
    raise cls(token, err_msg)


class LoxError(Exception):
    """ Base class to handle errors """

    token_types = loxtoken.TokenType

    def __init__(self, line: int, message: str, where: str = "") -> None:
        super().__init__(message)

        global had_error
        had_error = True
        self.line = line
        self.message = message
        self.where = where

    def report(self) -> str:
        return f"[line {self.line}] LoxError {self.where}: {self.message}"


class LoxParseError(Exception):
    """ Class to handle parser errors """

    def __init__(self, token: loxtoken.Token, message: str) -> None:
        super().__init__(message)

        global had_error
        had_error = True
        self.token = token
        self.message = message

    def report(self) -> str:
        if self.token.tok_type == LoxError.token_types.EOF:
            return f'[line {self.token.line}] Parse Error at end: {self.message}'
        else:
            return f"[line {self.token.line}] Parse Error at '{self.token.lexeme}': {self.message}"


class LoxRuntimeError(RuntimeError):
    """ Class to handle interpreter errors """

    def __init__(self, token: loxtoken.Token, message: str) -> None:
        super().__init__(message)

        global had_runtime_error
        had_runtime_error = True
        self.token = token
        self.message = message

    def report(self) -> str:
        return f'[line {self.token.line}] {self.token.lexeme} Runtime Error: {self.message}'


class Return(RuntimeError):
    """ Class to handle interpreter errors """

    def __init__(self, value: object) -> None:
        super().__init__()

        self.value = value
