from typing import List
from string import ascii_lowercase
from subprocess import getoutput
from os import walk
from ctypes import c_float
from argparse import ArgumentParser

from folders_types import CommandType, ExpressionType, TypeType, Command, Expression, If, \
    While, Declare, Let, Print, Input, Lit, IntLit, FloatLit, StrLit, CharLit, EqualTo, \
        LessThan, GreaterThan, Add, Subtract, Multiply, Divide, Variable

from parser import program_parser

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
                        assert(isinstance(expr, FloatLit))
                        self.encode_float(expr.value, e[2])

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
        byte_repr = bytes(c_float(value))[::-1]
        for byte in byte_repr:
            self.encode_nibble(byte >> 4, dest)
            self.encode_nibble(byte & 0xf, dest)

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

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--input", "-i", help="Input folderscript program", required=True)
    arg_parser.add_argument("--output", "-o", help="Output directory", required=True)
    arg_parser.add_argument("--verbose", "-v", help="Verbose mode", action="store_true")
    args = arg_parser.parse_args()

    with open(args.input, "r") as f:
        script = f.read()

    parsed = program_parser.parse(script)

    build_dir = args.output
    compiler = FoldersCompiler()
    compiler.compile(parsed, True, build_dir)

    if args.verbose:
        folders_created = len([x for x in walk(build_dir)]) - 1
        print(f"Program compiled to {folders_created} folders")
