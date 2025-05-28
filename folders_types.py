from enum import IntEnum

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
