from os import scandir
from typing import Dict
from folders_types import CommandType, ExpressionType, TypeType

dir_cache = {}
len_cache = {}

def get_dir(dir: str):
    if dir in dir_cache:
        return dir_cache[dir]
    dirs = sorted([d.path for d in scandir(dir) if d.is_dir()])
    dir_cache[dir] = dirs
    return dirs

def get_dir_count(dir: str):
    if dir in len_cache:
        return len_cache[dir]
    dir_len = len([d.path for d in scandir(dir) if d.is_dir()])
    len_cache[dir] = dir_len
    return dir_len

class Var:
    def __init__(self, type: TypeType):
        self.type = type

        match type:
            case TypeType.Int:
                self.value = 0
            case TypeType.Char:
                self.value = ''
            case TypeType.String:
                self.value = ''
            case TypeType.Float:
                self.value = 0

    def update(self, value):
        match self.type:
            case TypeType.Int:
                self.value = int(value)
            case TypeType.Char:
                self.value = str(value)[0]
            case TypeType.String:
                self.value = str(value)
            case TypeType.Float:
                self.value = float(value)

class Interpreter:
    def __init__(self):
        self.vars: Dict[str, Var] = {}

    def execute_commands(self, commands_dir: str):
        command_paths = get_dir(commands_dir)
        for command_dir in command_paths:
            self.execute_command(command_dir)

    def execute_command(self, command_dir: str):
        c = get_dir(command_dir)
        assert(len(c) >= 2)

        command_type = c[0]
        match get_dir_count(command_type):
            case CommandType.If:
                assert(len(c) == 3)
                condition = self.eval_expression(c[1])
                if condition:
                    self.execute_commands(c[2])

            case CommandType.While:
                assert(len(c) == 3)
                while self.eval_expression(c[1]):
                    self.execute_commands(c[2])

            case CommandType.Declare:
                assert(len(c) == 3)
                type_type = TypeType(get_dir_count(c[1]))
                var_name = self.eval_str(c[2])
                assert(var_name not in self.vars)
                self.vars[var_name] = Var(type_type)

            case CommandType.Let:
                assert(len(c) == 3)
                var_name = self.eval_str(c[1])
                assert(var_name in self.vars)

                expr_value = self.eval_expression(c[2])
                self.vars[var_name].update(expr_value)

            case CommandType.Print:
                value = self.eval_expression(c[1])
                print(value, end="")

            case CommandType.Input:
                var_name = self.eval_str(c[1])
                assert(var_name in self.vars)

                input_value = input()
                self.vars[var_name].update(input_value)

            case _:
                raise Exception(f"Invalid command: {command_type}")

    def eval_expression(self, expr_dir: str):
        e = get_dir(expr_dir)
        assert(len(e) >= 2)

        expr_type = e[0]
        match get_dir_count(expr_type):
            case ExpressionType.Variable:
                var_name = self.eval_str(e[1])
                assert(var_name in self.vars)
                return self.vars[var_name].value

            case ExpressionType.Add:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return lhs + rhs

            case ExpressionType.Subtract:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return lhs - rhs

            case ExpressionType.Multiply:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return lhs * rhs

            case ExpressionType.Divide:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return lhs // rhs

            case ExpressionType.LiteralValue:
                assert(len(e) == 3)
                lit_type = get_dir_count(e[1])
                match lit_type:
                    case TypeType.Int:
                        return self.eval_int(e[2])

                    case TypeType.Float:
                        return self.eval_float(e[2])

                    case TypeType.String:
                        return self.eval_str(e[2])

                    case TypeType.Char:
                        return self.eval_char(e[2])

                    case _:
                        raise Exception(f"Invalid literal: {lit_type}")

            case ExpressionType.EqualTo:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return int(lhs == rhs)

            case ExpressionType.GreaterThan:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return int(lhs > rhs)

            case ExpressionType.LessThan:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                return int(lhs < rhs)

            case _:
                raise Exception(f"Invalid expression: {expr_type}")


    def eval_int(self, int_dir: str):
        v = get_dir(int_dir)
        assert(len(v) == 8)

        value = 0
        for i in range(8):
            shift = 28 - (i * 4)
            value |= self.eval_nibble(v[i]) << shift

        if value >= 0x80000000:
            value = -((value ^ 0xffffffff) + 1)

        return value

    def eval_str(self, str_dir: str):
        bs = get_dir(str_dir)
        value = bytearray([])

        for byte_dir in bs:
            nibble_dirs = get_dir(byte_dir)
            assert(len(nibble_dirs) == 2)
            value.append((self.eval_nibble(nibble_dirs[0]) << 4) | self.eval_nibble(nibble_dirs[1]))

        return value.decode("utf-8")

    def eval_char(self, char_dir: str):
        nibble_dirs = get_dir(char_dir)
        assert(len(nibble_dirs) == 2)
        return chr((self.eval_nibble(nibble_dirs[0]) << 4) | self.eval_nibble(nibble_dirs[1]))

    def eval_float(self, float_dir: str):
        pass

    def eval_nibble(self, nibble_dir: str):
        n = get_dir(nibble_dir)
        assert(len(n) == 4)

        nibble = 0
        for i, bit_dir in enumerate(n):
            nibble |= get_dir_count(bit_dir) << (3 - i)
        return nibble


program_dir = "build"
interpreter = Interpreter()
interpreter.execute_commands(program_dir)
