from typing import List, Dict, Optional

import loxtoken
from loxerror import LoxError, raise_error


class Scanner:
    """ Scan source into tokens """

    # Dictionary of tokens
    token_types = loxtoken.TokenType

    lex: Dict[str, loxtoken.TokenType] = token_types.create_dict(["(", ")", "{", "}", ",", ".", "-", "+", ";", "*",
                                                                  "=", "==", "!", "!=", "<", "<=", ">", ">=", "/"])
    keywords: Dict[str, loxtoken.TokenType] = token_types.create_dict(["and", "class", "else", "false", "for", "fun",
                                                                       "if", "nil", "or", "print", "return", "super",
                                                                       "this", "true", "var", "while"])

    def __init__(self) -> None:

        self.source: str = ""  # source text
        self.tokens: List[loxtoken.Token] = list()  # output list of tokens
        self.start: int = 0  # offset of first char in current token
        self.current: int = 0  # current offset in string
        self.line: int = 1  # current line in source

    def scan_tokens(self, source: str) -> List[loxtoken.Token]:
        """ Main scanner
            Returns list of tokens """

        self.source = source
        self.line = 1
        self.tokens = list()
        self.start = 0
        self.current = 0
        while not self.is_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(loxtoken.Token(Scanner.token_types.EOF, "", None, self.line))
        return self.tokens

    def is_end(self) -> bool:
        """ Return True if end of source string """
        return self.current >= len(self.source)

    def get_next(self) -> str:
        """ Return character and update position to next """
        self.current += 1
        return self.source[self.current - 1]

    def char_at(self, pos: int) -> str:
        """ Return character at pos """
        return self.source[pos]

    def peek(self) -> str:
        """ Return character at pos without updating """
        if self.is_end():
            return '\n'
        else:
            return self.source[self.current]

    @property
    def peek_next(self) -> str:
        """ Return character one ahead without updating """
        if self.current + 1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        """ Return True if next character is expected character """
        if self.is_end() or self.char_at(self.current) != expected:
            return False
        else:
            self.current += 1
            return True

    def scan_token(self) -> None:
        """ Scan source and append tokens """

        char: str = self.get_next()

        if char in "!=<>" and self.match("="):
            char = char + "="
        elif char == "/" and self.match("/"):
            while self.peek() != '\n' and not self.is_end():
                self.get_next()
            return
        elif char == "\n":
            self.line += 1
        if char in Scanner.lex:
            tok = Scanner.lex.get(char, None)
            if tok is not None:
                self.add_token(tok, None, self.line)
        elif char == '"':
            self.get_string()
        elif char.isdigit():
            self.get_number()
        elif self.is_valid_first(char):
            self.get_identifier()

        elif not char.isspace():
            raise_error(LoxError, self.line, f'Unexpected character: {char}')

    def get_string(self) -> None:
        """ Process literal string and add token 
            Increase line no if required """

        while self.peek() != '"' and not self.is_end():
            char: str = self.get_next()
            if char == "\n":
                self.line += 1
        if self.is_end():
            raise_error(LoxError, self.line, "Unterminated string.")
            return
        value: str = self.source[self.start + 1: self.current]
        self.add_token(Scanner.token_types.STRING, value, self.line)
        self.get_next()

    def get_number(self) -> None:
        """ Process number and add token """

        while self.peek().isdigit() and not self.is_end():
            self.get_next()
        if self.peek() == "." and self.peek_next.isdigit():
            self.get_next()
        while self.peek().isdigit() and not self.is_end():
            self.get_next()
        value: float = float(self.source[self.start: self.current])
        self.add_token(Scanner.token_types.NUMBER, value, self.line)

    @staticmethod
    def is_valid_first(char) -> bool:
        """ Check first letter is alpha or _ """

        return char.isalpha() or char == "_"

    def get_identifier(self) -> None:
        """ Process identifier and add token """

        while self.peek().isalnum():
            self.get_next()
        value: str = self.source[self.start: self.current]
        tok_type: loxtoken.TokenType = Scanner.keywords.get(value, Scanner.token_types.IDENTIFIER)
        self.add_token(tok_type, value, self.line)

    def add_token(self, tok_type: loxtoken.TokenType, literal: Optional[object], line: int = 0) -> None:
        """ Append token to list """

        text: str = self.source[self.start:self.current]
        self.tokens.append(loxtoken.Token(tok_type, text, literal, line))
