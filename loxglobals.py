import time

from loxenvironment import Environment
from loxcallable import LoxCallable


class Globals:
    """ Class defining environment with global functions """

    def __init__(self):
        self.globals: Environment = Environment()

        self.globals.define("clock", type("Clock",
                                          (LoxCallable,),
                                          {"arity": lambda: 0,
                                           "call": lambda interpreter, arguments: float(time.time_ns() // 1000000),
                                           "__str__": lambda: "<native fn>"}))
