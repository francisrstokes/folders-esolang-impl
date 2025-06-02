from enum import IntEnum
from typing import List

class CommandType(IntEnum):
    If           = 0
    While        = 1
    Declare      = 2
    Let          = 3
    Print        = 4
    Input        = 5

class ExpressionType(IntEnum):
    Variable     = 0
    Add          = 1
    Subtract     = 2
    Multiply     = 3
    Divide       = 4
    LiteralValue = 5
    EqualTo      = 6
    GreaterThan  = 7
    LessThan     = 8

class TypeType(IntEnum):
    Int          = 0
    Float        = 1
    String       = 2
    Char         = 3

    @staticmethod
    def from_name(name: str):
        match name.lower():
            case "int":
                return TypeType.Int
            case "float":
                return TypeType.Float
            case "string":
                return TypeType.String
            case "char":
                return TypeType.Char
            case _:
                assert(False)

class Command:
    def __init__(self, command_type: CommandType):
        self.command_type = command_type

class Expression:
    def __init__(self, expr_type: ExpressionType):
        self.expr_type = expr_type

# Commands
class If(Command):
    def __init__(self, expr: Expression, commands: List[Command]):
        super().__init__(CommandType.If)
        self.expr = expr
        self.commands = commands

    def __repr__(self):
        command_strs = ",".join([f"{c}" for c in self.commands])
        return f"If({self.expr}, [{command_strs}])"

class While(Command):
    def __init__(self, expr: Expression, commands: List[Command]):
        super().__init__(CommandType.While)
        self.expr = expr
        self.commands = commands

    def __repr__(self):
        command_strs = ",".join([f"{c}" for c in self.commands])
        return f"While({self.expr}, [{command_strs}])"

class Declare(Command):
    def __init__(self, type: TypeType, var_name: str):
        super().__init__(CommandType.Declare)
        self.type = type
        self.var_name = var_name

    def __repr__(self):
        return f"Declare({self.type}, {self.var_name})"

class Let(Command):
    def __init__(self, var_name: str, value: Expression):
        super().__init__(CommandType.Let)
        self.var_name = var_name
        self.value = value

    def __repr__(self):
        return f"Let({self.var_name}, {self.value})"

class Print(Command):
    def __init__(self, expr: Expression):
        super().__init__(CommandType.Print)
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"

class Input(Command):
    def __init__(self, var_name: str):
        super().__init__(CommandType.Input)
        self.var_name = var_name

    def __repr__(self):
        return f"Input({self.var_name})"

# Expressions (Literals)
class Lit(Expression):
    def __init__(self, lit_type: TypeType):
        super().__init__(ExpressionType.LiteralValue)
        self.lit_type = lit_type

class IntLit(Lit):
    def __init__(self, value: int):
        assert(value >= -2147483647 and value <= 0xffffffff)

        super().__init__(TypeType.Int)

        self.value = value
        if self.value < 0:
            self.value = (-self.value ^ 0xffffffff) + 1

    def __repr__(self):
        return f"IntLit({self.value})"

class FloatLit(Lit):
    def __init__(self, value: float):
        super().__init__(TypeType.Float)
        self.value = value

    def __repr__(self):
        return f"FloatLit({self.value})"

class StrLit(Lit):
    def __init__(self, value: str):
        super().__init__(TypeType.String)
        self.value = value

    def __repr__(self):
        return f"StrLit(\"{self.value}\")"

class CharLit(Lit):
    def __init__(self, value: str):
        assert(len(value) == 1)
        super().__init__(TypeType.Char)
        self.value = value

    def __repr__(self):
        return f"CharLit('{self.value}')"

# Expressions (Comparisons)
class EqualTo(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.EqualTo)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"EqualTo({self.lhs}, {self.rhs})"

class LessThan(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.LessThan)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"LessThan({self.lhs}, {self.rhs})"

class GreaterThan(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.GreaterThan)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"GreaterThan({self.lhs}, {self.rhs})"

# Expressions (Arithmetic)
class Add(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Add)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Add({self.lhs}, {self.rhs})"

class Subtract(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Subtract)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Subtract({self.lhs}, {self.rhs})"

class Multiply(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Multiply)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Multiply({self.lhs}, {self.rhs})"

class Divide(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Divide)
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Divide({self.lhs}, {self.rhs})"

# Expressions (Variable)
class Variable(Expression):
    def __init__(self, var_name: str):
        super().__init__(ExpressionType.Variable)
        self.var_name = var_name

    def __repr__(self):
        return f"Var({self.var_name})"
