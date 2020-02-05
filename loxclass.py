from typing import List, Dict, Optional, TYPE_CHECKING

import loxcallable
import loxtoken
from loxerror import LoxRuntimeError
from loxerror import raise_error

if TYPE_CHECKING:
    import loxinterpreter
    import loxtoken


class LoxClass(loxcallable.LoxCallable):

    def __init__(self, name: str, superclass: 'LoxClass', methods=None):
        super().__init__()
        if methods is None:
            methods = dict()
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self) -> str:
        """ Return class as string """
        return f"{self.name} class"

    def call(self, interpreter: 'loxinterpreter.Interpreter', arguments: List[object]) -> 'LoxInstance':
        """ Call the class """
        instance: 'LoxInstance' = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        """ Returns no of parameters required """
        initializer = self.find_method("init")
        if initializer is not None:
            return initializer.arity()
        return 0

    def find_method(self, name: str) -> Optional[loxcallable.LoxFunction]:
        """ Find and return class method """
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None


class LoxInstance:

    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: Dict[str, object] = dict()

    def __str__(self) -> str:
        """ Return class instance as string """
        return f"{self.klass.name} instance"

    def get(self, name: loxtoken.Token):
        """ Get property """
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise_error(LoxRuntimeError, name, "Undefined property '" + name.lexeme + "'.")

    def set(self, name: loxtoken.Token, value: object):
        """ Set value of property """
        self.fields[name.lexeme] = value
