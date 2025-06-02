from os import scandir
from typing import Dict, Callable, List
from struct import unpack
from argparse import ArgumentParser
from folders_types import CommandType, ExpressionType, TypeType

dir_cache = {}
len_cache = {}
expr_type_cache = {}
expr_cache = {}

def get_dir(dir: str) -> List[str]:
    if dir in dir_cache:
        return dir_cache[dir]
    dirs = sorted([d.path for d in scandir(dir) if d.is_dir()])
    dir_cache[dir] = dirs
    return dirs

def get_dir_count(dir: str) -> int:
    if dir in len_cache:
        return len_cache[dir]
    dir_len = len([d.path for d in scandir(dir) if d.is_dir()])
    len_cache[dir] = dir_len
    return dir_len

def get_dir_count_no_cache(dir: str):
    return len([d.path for d in scandir(dir) if d.is_dir()])

def as_i32(v: int):
    v &= 0xffffffff
    if v >= 0x80000000:
        return -((v ^ 0xffffffff) + 1)
    return v

def compare_on_type(compare_fn: Callable[[int | float | str, int | float | str], int]):
    def compare(lhs: int | float | str, rhs: int | float | str, lhs_type: TypeType, rhs_type: TypeType):
        if lhs_type == rhs_type:
            return int(compare_fn(lhs, rhs))

        match lhs_type:
            case TypeType.Int | TypeType.Float:
                assert(rhs_type != TypeType.String)
                match rhs_type:
                    case TypeType.Int | TypeType.Float:
                        return int(compare_fn(lhs, rhs))
                    case TypeType.Char:
                        return int(compare_fn(lhs, ord(rhs))) # type: ignore
            case TypeType.String:
                assert(rhs_type not in [TypeType.Int, TypeType.Float])
                return int(compare_fn(lhs, rhs))
            case TypeType.Char:
                match rhs_type:
                    case TypeType.Int | TypeType.Float:
                        return int(compare_fn(ord(lhs), rhs)) # type: ignore
                    case _:
                        return int(compare_fn(lhs, ord(rhs))) # type: ignore
    return compare

eq = compare_on_type(lambda x, y: x == y)
lt = compare_on_type(lambda x, y: x < y) # type: ignore
gt = compare_on_type(lambda x, y: x > y) # type: ignore

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
                self.value = 0.0

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
                var_name = self.eval_str(command_dir, c[2])
                assert(var_name not in self.vars)
                self.vars[var_name] = Var(type_type)

            case CommandType.Let:
                assert(len(c) == 3)
                var_name = self.eval_str(command_dir, c[1])
                assert(var_name in self.vars)

                expr_value = self.eval_expression(c[2])
                self.vars[var_name].value = expr_value # type: ignore

            case CommandType.Print:
                value = self.eval_expression(c[1])
                print(value, end="")

            case CommandType.Input:
                var_name = self.eval_str(command_dir, c[1])
                assert(var_name in self.vars)

                input_value = input()
                match self.vars[var_name].type:
                    case TypeType.Int:
                        self.vars[var_name].value = int(input_value)
                    case TypeType.Char:
                        self.vars[var_name].value = str(input_value)[0]
                    case TypeType.String:
                        self.vars[var_name].value = str(input_value)
                    case TypeType.Float:
                        self.vars[var_name].value = float(input_value)

            case _:
                raise Exception(f"Invalid command: {command_type}")

    def expression_is_literal(self, expr_dir: str):
        e = get_dir(expr_dir)
        return get_dir_count(e[0]) == ExpressionType.LiteralValue

    def eval_expression(self, expr_dir: str):
        if expr_dir in expr_cache:
            return expr_cache[expr_dir]

        e = get_dir(expr_dir)
        assert(len(e) >= 2)

        expr_type = e[0]
        match get_dir_count(expr_type):
            case ExpressionType.Variable:
                var_name = self.eval_str(expr_dir + "_var", e[1])
                assert(var_name in self.vars)
                return self.vars[var_name].value

            case ExpressionType.Add:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])

                expr_type = self.determine_expr_type(expr_dir)
                match expr_type:
                    case TypeType.Int:
                        value = as_i32(lhs + rhs)
                    case TypeType.String | TypeType.Float:
                        value = lhs + rhs
                    case TypeType.Char:
                        value = chr((ord(lhs) + ord(rhs)) & 0xff)

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.Subtract:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])

                expr_type = self.determine_expr_type(expr_dir)
                assert(expr_type != TypeType.String)

                match expr_type:
                    case TypeType.Int:
                        value = as_i32(lhs - rhs)
                    case TypeType.Float:
                        value = lhs - rhs
                    case TypeType.Char:
                        value = chr((ord(lhs) - ord(rhs)) & 0xff)

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.Multiply:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])

                expr_type = self.determine_expr_type(expr_dir)
                assert(not expr_type in [TypeType.String, TypeType.Char])

                match expr_type:
                    case TypeType.Int:
                        value = as_i32(lhs * rhs)
                    case _:
                        value = lhs * rhs

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.Divide:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])

                expr_type = self.determine_expr_type(expr_dir)
                assert(expr_type != TypeType.String)

                match expr_type:
                    case TypeType.Int:
                        value = as_i32(lhs // rhs)
                    case TypeType.Float:
                        value = lhs / rhs
                    case TypeType.Char:
                        value = chr(ord(lhs) // ord(rhs))

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.LiteralValue:
                assert(len(e) == 3)
                lit_type = get_dir_count(e[1])
                match lit_type:
                    case TypeType.Int:
                        value = self.eval_int(e[2])

                    case TypeType.Float:
                        value = self.eval_float(e[2])

                    case TypeType.String:
                        return self.eval_str(expr_dir, e[2])

                    case TypeType.Char:
                        value = self.eval_char(e[2])

                    case _:
                        raise Exception(f"Invalid literal: {lit_type}")

                expr_cache[expr_dir] = value
                return value

            case ExpressionType.EqualTo:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                lhs_type = self.determine_expr_type(e[1])
                rhs_type = self.determine_expr_type(e[2])

                value = eq(lhs, rhs, lhs_type, rhs_type)

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.GreaterThan:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                lhs_type = self.determine_expr_type(e[1])
                rhs_type = self.determine_expr_type(e[2])

                value = gt(lhs, rhs, lhs_type, rhs_type)

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case ExpressionType.LessThan:
                assert(len(e) == 3)
                lhs = self.eval_expression(e[1])
                rhs = self.eval_expression(e[2])
                lhs_type = self.determine_expr_type(e[1])
                rhs_type = self.determine_expr_type(e[2])

                value = lt(lhs, rhs, lhs_type, rhs_type)

                if self.expression_is_literal(e[1]) and self.expression_is_literal(e[2]):
                    expr_cache[expr_dir] = value

                return value

            case _:
                raise Exception(f"Invalid expression: {expr_type}")

    def determine_expr_type(self, expr_dir: str) -> TypeType:
        if expr_dir in expr_type_cache:
            return expr_type_cache[expr_dir]
        e = get_dir(expr_dir)
        assert(len(e) >= 2)

        expr_type = e[0]
        match get_dir_count(expr_type):
            case ExpressionType.Variable:
                var_name = self.eval_str(expr_dir + "_var", e[1])
                assert(var_name in self.vars)
                expr_type_cache[expr_dir] = self.vars[var_name].type
                return expr_type_cache[expr_dir]

            case ExpressionType.Add:
                assert(len(e) == 3)
                lhs = self.determine_expr_type(e[1])
                rhs = self.determine_expr_type(e[2])
                if lhs != rhs:
                    assert(lhs == TypeType.String and rhs == TypeType.Char)
                    expr_type_cache[expr_dir] = TypeType.String
                    return expr_type_cache[expr_dir]
                expr_type_cache[expr_dir] = lhs
                return expr_type_cache[expr_dir]

            case ExpressionType.Subtract | ExpressionType.Multiply | ExpressionType.Divide:
                assert(len(e) == 3)
                lhs = self.determine_expr_type(e[1])
                rhs = self.determine_expr_type(e[2])
                assert(lhs == rhs)
                expr_type_cache[expr_dir] = lhs
                return expr_type_cache[expr_dir]

            case ExpressionType.LiteralValue:
                expr_type_cache[expr_dir] = TypeType(get_dir_count(e[1]))
                return expr_type_cache[expr_dir]

            case ExpressionType.EqualTo | ExpressionType.GreaterThan | ExpressionType.LessThan:
                expr_type_cache[expr_dir] = TypeType.Int
                return expr_type_cache[expr_dir]

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

    def eval_str(self, expr_dir: str, str_dir: str):
        if expr_dir in expr_cache:
            return expr_cache[expr_dir]

        bs = get_dir(str_dir)
        value = bytearray([])

        for byte_dir in bs:
            nibble_dirs = get_dir(byte_dir)
            assert(len(nibble_dirs) == 2)
            value.append((self.eval_nibble(nibble_dirs[0]) << 4) | self.eval_nibble(nibble_dirs[1]))

        value = value.decode("utf-8")
        expr_cache[expr_dir] = value
        return value

    def eval_char(self, char_dir: str):
        nibble_dirs = get_dir(char_dir)
        assert(len(nibble_dirs) == 2)
        value = chr((self.eval_nibble(nibble_dirs[0]) << 4) | self.eval_nibble(nibble_dirs[1]))
        return value

    def eval_float(self, float_dir: str):
        v = get_dir(float_dir)
        assert(len(v) == 8)

        raw_bytes = bytearray([])
        for i in range(8):
            nibble = self.eval_nibble(v[i])
            if i % 2 == 0:
                raw_bytes.append(nibble << 4)
            else:
                raw_bytes[i//2] |= nibble

        value = unpack("f", raw_bytes[::-1])[0]
        return value

    def eval_nibble(self, nibble_dir: str):
        n = get_dir(nibble_dir)
        assert(len(n) == 4)

        nibble = 0
        for i, bit_dir in enumerate(n):
            nibble |= get_dir_count_no_cache(bit_dir) << (3 - i)
        return nibble

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--input", "-i", help="Input folders directory", required=True)
    args = arg_parser.parse_args()

    program_dir = args.input
    interpreter = Interpreter()
    interpreter.execute_commands(program_dir)
