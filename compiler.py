from typing import List
from string import ascii_lowercase
from subprocess import getoutput
from os import walk

from folders_types import CommandType, ExpressionType, TypeType

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

class While(Command):
    def __init__(self, expr: Expression, commands: List[Command]):
        super().__init__(CommandType.While)
        self.expr = expr
        self.commands = commands

class Declare(Command):
    def __init__(self, type: TypeType, var_name: str):
        super().__init__(CommandType.Declare)
        self.type = type
        self.var_name = var_name

class Let(Command):
    def __init__(self, var_name: str, value: Expression):
        super().__init__(CommandType.Let)
        self.var_name = var_name
        self.value = value

class Print(Command):
    def __init__(self, expr: Expression):
        super().__init__(CommandType.Print)
        self.expr = expr

class Input(Command):
    def __init__(self, var_name: str):
        super().__init__(CommandType.Input)
        self.var_name = var_name

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

class FloatLit(Lit):
    def __init__(self, value: float):
        super().__init__(TypeType.Float)
        self.value = value

class StrLit(Lit):
    def __init__(self, value: str):
        super().__init__(TypeType.String)
        self.value = value

class CharLit(Lit):
    def __init__(self, value: str):
        assert(len(value) == 1)
        super().__init__(TypeType.Char)
        self.value = value

# Expressions (Comparisons)
class EqualTo(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.EqualTo)
        self.lhs = lhs
        self.rhs = rhs

class LessThan(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.LessThan)
        self.lhs = lhs
        self.rhs = rhs

class GreaterThan(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.GreaterThan)
        self.lhs = lhs
        self.rhs = rhs

# Expressions (Arithmetic)
class Add(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Add)
        self.lhs = lhs
        self.rhs = rhs

class Subtract(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Subtract)
        self.lhs = lhs
        self.rhs = rhs

class Multiply(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Multiply)
        self.lhs = lhs
        self.rhs = rhs

class Divide(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        super().__init__(ExpressionType.Divide)
        self.lhs = lhs
        self.rhs = rhs

# Expressions (Variable)
class Variable(Expression):
    def __init__(self, var_name: str):
        super().__init__(ExpressionType.Variable)
        self.var_name = var_name

encoded_nibbles = [ list(map(lambda b: [[]] if b == '1' else [], list(f"{i:04b}"))) for i in range(16) ]

# Compiler
class FoldersCompiler:
    def __init__(self):
        self.level = 0

    def encode_type_value(self, type_value: int, dest: List):
        dest.extend([ [] for _ in range(type_value) ])

    def encode_commands(self, commands: List[Command], dest: List):
        for c in commands:
            self.encode_command(c, dest)

    def encode_command(self, command: Command, dest: List):
        c = [[], []]
        dest.append(c)
        self.encode_type_value(command.command_type, c[0])

        match command.command_type:
            case CommandType.If:
                assert(isinstance(command, If))
                c.append([])
                self.encode_expression(command.expr, c[1])
                self.encode_commands(command.commands, c[2])

            case CommandType.While:
                assert(isinstance(command, While))
                c.append([])
                self.encode_expression(command.expr, c[1])
                self.encode_commands(command.commands, c[2])

            case CommandType.Declare:
                assert(isinstance(command, Declare))
                c.append([])
                self.encode_type_value(command.type, c[1])
                self.encode_string(command.var_name, c[2])

            case CommandType.Let:
                assert(isinstance(command, Let))
                c.append([])
                self.encode_string(command.var_name, c[1])
                self.encode_expression(command.value, c[2])

            case CommandType.Print:
                assert(isinstance(command, Print))
                self.encode_expression(command.expr, c[1])

            case CommandType.Input:
                assert(isinstance(command, Input))
                self.encode_string(command.var_name, c[1])


    def encode_expression(self, expr: Expression, dest: List):
        e = dest
        e.extend([[], []])
        self.encode_type_value(expr.expr_type, e[0])

        match expr.expr_type:
            case ExpressionType.Variable:
                assert(isinstance(expr, Variable))
                self.encode_string(expr.var_name, e[1])

            case ExpressionType.Add:
                assert(isinstance(expr, Add))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.Subtract:
                assert(isinstance(expr, Subtract))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.Multiply:
                assert(isinstance(expr, Multiply))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.Divide:
                assert(isinstance(expr, Divide))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.LiteralValue:
                assert(isinstance(expr, Lit))
                self.encode_type_value(expr.lit_type, e[1])
                e.append([])

                match expr.lit_type:
                    case TypeType.Int:
                        assert(isinstance(expr, IntLit))
                        self.encode_int(expr.value, e[2])

                    case TypeType.Float:
                        pass

                    case TypeType.String:
                        assert(isinstance(expr, StrLit))
                        self.encode_string(expr.value, e[2])

                    case TypeType.Char:
                        assert(isinstance(expr, CharLit))
                        self.encode_char(expr.value, e[2])

            case ExpressionType.EqualTo:
                assert(isinstance(expr, EqualTo))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.GreaterThan:
                assert(isinstance(expr, GreaterThan))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

            case ExpressionType.LessThan:
                assert(isinstance(expr, LessThan))
                e.append([])
                self.encode_expression(expr.lhs, e[1])
                self.encode_expression(expr.rhs, e[2])

    def encode_int(self, value: int, dest: List):
        for i in range(8):
            shift = 28 - (i * 4)
            self.encode_nibble((value >> shift) & 0xf, dest)

    def encode_string(self, value: str, dest: List):
        for byte in value.encode("utf-8"):
            dest.append([])
            self.encode_nibble(byte >> 4, dest[-1])
            self.encode_nibble(byte & 0xf, dest[-1])

    def encode_char(self, value: str, dest: List):
        char_value = ord(value[0]) & 0xff
        self.encode_nibble(char_value >> 4, dest)
        self.encode_nibble(char_value & 0xf, dest)

    def encode_float(self, value: float, dest: List):
        pass

    def encode_nibble(self, value: int, dest: List):
        dest.append(encoded_nibbles[value])

    @staticmethod
    def folder_name_from_index(index: int):
        assert(index >= 0)
        alphabet = ascii_lowercase
        base = len(alphabet)
        prefix_len = (index // base)
        prefix = 'z' * prefix_len
        index -= base * prefix_len
        return prefix + alphabet[index]

    @staticmethod
    def list_to_names(l: list) -> List[str]:
        return [FoldersCompiler.folder_name_from_index(i) for i in range(len(l))]

    @staticmethod
    def _write_structure_to_disk(base_dir: str, encoded: list):
        if len(encoded) == 0:
            return

        paths = [f"{base_dir}/{name}" for name in FoldersCompiler.list_to_names(encoded)]
        getoutput(f"mkdir -p {' '.join(paths)}")
        for path, sublist in zip(paths, encoded):
            FoldersCompiler._write_structure_to_disk(path, sublist)

    def compile(self, program: List[Command], write_to_disk = False, build_dir = "build"):
        out = []
        self.encode_commands(program, out)

        if write_to_disk:
            getoutput(f"rm -rf {build_dir}")
            getoutput(f"mkdir -p {build_dir}")
            FoldersCompiler._write_structure_to_disk(build_dir, out)

        return out

test_program: List[Command] = [
    # Serpinsky
    Declare(TypeType.Int, "x"),
    Declare(TypeType.Int, "y"),
    Declare(TypeType.Int, "xm"),
    Declare(TypeType.Int, "ym"),
    Declare(TypeType.Int, "i"),
    Declare(TypeType.Int, "j"),
    Declare(TypeType.Int, "p"),
    Declare(TypeType.Int, "xs"),
    Declare(TypeType.Int, "ys"),
    Declare(TypeType.Int, "xb"),
    Declare(TypeType.Int, "yb"),
    Declare(TypeType.Int, "xy"),
    Declare(TypeType.Char, "v"),

    Print(StrLit("x max >> ")),
    Input("xm"),
    Print(StrLit("y max >> ")),
    Input("ym"),

    While(LessThan(Variable("y"), Variable("ym")), [
        Let("x", IntLit(0)),
        While(LessThan(Variable("x"), Variable("xm")), [
            Let("i", IntLit(0)),
            Let("v", CharLit('v')),

            While(LessThan(Variable("i"), IntLit(7)), [
                Let("j", IntLit(0)),
                Let("p", IntLit(1)),

                While(LessThan(Variable("j"), Variable("i")), [
                    Let("p", Multiply(Variable("p"), IntLit(2))),
                    Let("j", Add(Variable("j"), IntLit(1))),
                ]),

                Let("xs", Divide(Variable("x"), Variable("p"))),
                Let("ys", Divide(Variable("y"), Variable("p"))),

                Let("xb", Subtract(Variable("xs"), Multiply(Divide(Variable("xs"), IntLit(2)), IntLit(2)))),
                Let("yb", Subtract(Variable("ys"), Multiply(Divide(Variable("ys"), IntLit(2)), IntLit(2)))),

                Let("xy", Add(Variable("xb"), Variable("yb"))),

                If(EqualTo(Variable("xy"), IntLit(2)), [
                    Let("v", CharLit(' ')),
                ]),

                Let("i", Add(Variable("i"), IntLit(1))),
            ]),

            Print(Variable("v")),

            Let("x", Add(Variable("x"), IntLit(1))),
        ]),
        Print(CharLit("\n")),
        Let("y", Add(Variable("y"), IntLit(1))),
    ]),
]

build_dir = 'build'
compiler = FoldersCompiler()
compiler.compile(test_program, True, build_dir)

folders_created = len([x for x in walk(build_dir)]) - 1
print(f"Program compiled to {folders_created} folders")

# json_encoded = []
# compiler.encode_commands(test_program, json_encoded)
# with open(f"{build_dir}.json", "w") as f:
#     f.write(str(json_encoded))
#     f.write('\n')
