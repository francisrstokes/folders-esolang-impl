from os import scandir
from folders_types import CommandType

def get_dir(dir: str):
    return sorted([d.path for d in scandir(dir) if d.is_dir()])

def get_dir_count(dir: str):
    return len([d.path for d in scandir(dir) if d.is_dir()])

class Enumerator:
    def __init__(self):
        self.level = 0

    def push_level(self):
        self.level += 1

    def pop_level(self):
        self.level -= 1

    def log(self, command_type: str, command_dir: str, arg: str = ""):
        indent = " " * (4 * self.level)
        print(f"[{command_dir:<25}] {indent}{command_type}{f'({arg})' if len(arg) else ''}")

    def enumerate_commands(self, commands_dir: str):
        command_paths = get_dir(commands_dir)
        for command_dir in command_paths:
            self.enumerate_command(command_dir)

    def enumerate_command(self, command_dir: str):
        c = get_dir(command_dir)
        assert(len(c) >= 2)

        command_type = c[0]
        match get_dir_count(command_type):
            case CommandType.If:
                self.log("If", command_dir)
                assert(len(c) == 3)
                self.push_level()
                self.enumerate_commands(c[2])
                self.pop_level()

            case CommandType.While:
                self.log("While", command_dir)
                assert(len(c) == 3)
                self.push_level()
                self.enumerate_commands(c[2])
                self.pop_level()

            case CommandType.Declare:
                assert(len(c) == 3)
                var_name = self.eval_str(c[2])
                self.log("Declare", command_dir, var_name)

            case CommandType.Let:
                assert(len(c) == 3)
                var_name = self.eval_str(c[1])
                self.log("Let", command_dir, var_name)

            case CommandType.Print:
                self.log("Print", command_dir)

            case CommandType.Input:
                var_name = self.eval_str(c[1])
                self.log("Input", command_dir, var_name)

            case _:
                raise Exception(f"Invalid command: {command_type}")

    def eval_str(self, str_dir: str):
        bs = get_dir(str_dir)
        value = bytearray([])

        for byte_dir in bs:
            nibble_dirs = get_dir(byte_dir)
            assert(len(nibble_dirs) == 2)
            value.append((self.eval_nibble(nibble_dirs[0]) << 4) | self.eval_nibble(nibble_dirs[1]))

        return value.decode("utf-8")

    def eval_nibble(self, nibble_dir: str):
        n = get_dir(nibble_dir)
        assert(len(n) == 4)

        nibble = 0
        for i, bit_dir in enumerate(n):
            nibble |= get_dir_count(bit_dir) << (3 - i)
        return nibble


program_dir = "build"
enumerator = Enumerator()
enumerator.enumerate_commands(program_dir)
