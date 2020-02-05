from typing import List, TYPE_CHECKING

from loxenvironment import Environment
from loxerror import Return

if TYPE_CHECKING:
    import loxinterpreter


class LoxCallable:
    """ Base class for callable functions in lox """

    def __init__(self, funct: object = None) -> None:
        self.funct = funct

    def arity(self) -> int:
        """ Returns no of parameters required """
        pass

    def call(self, interpreter: 'loxinterpreter.Interpreter', arguments: List[object]) -> object:
        """ Run the function """
        pass


class LoxFunction(LoxCallable):
    """ Class to handle functions in lox """

    def __init__(self, declaration, closure: Environment, is_initializer: bool = False):
        super(LoxFunction, self).__init__(declaration)

        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer

    def bind(self, instance):
        """ Create new environment enclosing closure and define 'this' """
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter: 'loxinterpreter.Interpreter', arguments: List[object]) -> object:
        """ Run the function """
        environment: Environment = Environment(self.closure)
        i = 0
        for parameter in self.declaration.params:
            environment.define(parameter.lexeme, arguments[i])
            i += 1
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def arity(self) -> int:
        """ Returns no of parameters required """
        return len(self.declaration.params)

    def __str__(self) -> str:
        """ Return function as string """
        return f'<fn {self.declaration.name.lexeme} >'
