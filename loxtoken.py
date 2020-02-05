from typing import List, Dict, Optional

import enum


class TokenType(enum.Enum):
    """ Enumeration class for all tokens/keywords
        Extra field contains string value """

    def __new__(cls, keycode: int, symbol: str = "") -> 'TokenType':
        """ Allow extra field in each item """
        obj = object.__new__(cls)
        obj._value_ = keycode
        obj.symbol = symbol
        return obj

    def __init__(self, keycode, symbol):
        self.keycode = keycode
        self.symbol = symbol

    # Single-character tokens.                      
    LEFT_PAREN = (1, "(")
    RIGHT_PAREN = (2, ")")
    LEFT_BRACE = (3, "{")
    RIGHT_BRACE = (4, "}")
    COMMA = (5, ",")
    DOT = (6, ".")
    MINUS = (7, "-")
    PLUS = (8, "+")
    SEMICOLON = (9, ";")
    SLASH = (10, "/")
    STAR = (11, "*")

    # One or two character tokens.                  
    BANG = (20, "!")
    BANG_EQUAL = (21, "!=")
    EQUAL = (22, "=")
    EQUAL_EQUAL = (23, "==")
    GREATER = (24, ">")
    GREATER_EQUAL = (25, ">=")
    LESS = (26, "<")
    LESS_EQUAL = (27, "<=")

    # Literals.                                     
    IDENTIFIER = (30, "")
    STRING = (31, "")
    NUMBER = (32, "")

    # Keywords.                                     
    AND = (40, "and")
    CLASS = (41, "class")
    ELSE = (42, "else")
    FALSE = (43, "false")
    FUN = (44, "fun")
    FOR = (45, "for")
    IF = (46, "if")
    NIL = (47, "nil")
    OR = (48, "or")
    PRINT = (50, "print")
    RETURN = (51, "return")
    SUPER = (52, "super")
    THIS = (53, "this")
    TRUE = (54, "true")
    VAR = (55, "var")
    WHILE = (56, "while")

    EOF = (60, "eof")

    @staticmethod
    def create_dict(symbolset: List[str]) -> Dict[str, 'TokenType']:
        """ Create dictionary from items in symbolset """
        return {key: val for key in symbolset for val in TokenType if val.symbol == key}

    @staticmethod
    def create_list(symbolset: List[str]) -> List['TokenType']:
        """ Create list from items in symbolset """
        return [tok for sym in symbolset for tok in TokenType if tok.symbol == sym]


class Token:
    """ Token class """

    def __init__(self, tok_type: TokenType, lexeme: str, literal: object, line: int):
        self.tok_type = tok_type  # Token type
        self.lexeme = lexeme  # string from source
        self.literal = literal  # Token value
        self.line = line  # Line no in source

    def __str__(self) -> str:
        """ Used to print token """
        text: str = f'{self.tok_type.name} {self.lexeme}'
        if self.literal is None:
            text = f'{text} None '
        elif isinstance(self.literal, float):
            text = f'{text} {self.literal}'

        return f'Line: {self.line} - {text}'

    def to_string(self) -> Optional[str]:
        """ Token attributes as string """
        if self.tok_type is not None:
            return f'{self.tok_type.name} {self.lexeme} {self.literal}'
        return None

    def to_line(self) -> str:
        """ Used to print token line """
        return f'Line: {self.line}'
