from typing import Dict, Any

from loxerror import LoxRuntimeError, raise_error
from loxtoken import Token


class Environment:
    """ Class defining environments """

    def __init__(self, enclosing: 'Environment' = None) -> None:

        self.enclosing = enclosing
        self.values: Dict[str, object] = dict()

    def define(self, name: str, value: object = None) -> None:
        """ Add name and value to environment """
        self.values[name] = value

    def get_at(self, distance: int, name: str) -> Any:
        """ get value of token from environment at depth distance """
        return self.ancestor(distance).values.get(name)

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        """ assign value of token from environment at depth distance """
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> 'Environment':
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def get(self, name: Token) -> object:
        """ get value of token from nearest environment """
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise_error(LoxRuntimeError, name, f'Undefined variable {name.lexeme}.')
        return None

    def assign(self, name: Token, value: object) -> None:
        """ set value of name in nearest environment where it exits 
            otherwise return error """
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise_error(LoxRuntimeError, name, f'Undefined variable {name.lexeme}.')
