from typing import List, Union, Type
from parsy import string, regex, seq, forward_declaration, Parser, generate, eof, whitespace as ws
from folders_types import TypeType, If, While, Declare, Let, Print, Input, IntLit, FloatLit, StrLit, \
    CharLit, EqualTo, LessThan, GreaterThan, Add, Subtract, Multiply, Divide, Variable

parse_state = { "indent_level": 0 }

def possibly(p: Parser):
    return p.times(0, 1)

def zero_or_more(p: Parser):
    return p.at_least(0)

def one_or_more(p: Parser):
    return p.at_least(1)

@generate
def indent_parser():
    indent = " " * parse_state["indent_level"] * 4
    matched = yield string(indent)
    return matched

def indented(p: Parser):
    return indent_parser >> p

whitespace = regex(r"[ \t]+")
optional_whitespace = regex(r"[ \t]*")
newline = regex(r"\r\n|\r|\n")
identifier = regex(r"[a-zA-Z_][a-zA-Z0-9_]*")

def ows(p: Parser):
    return seq(optional_whitespace, p, optional_whitespace).map(lambda x: x[1])

def unescape(s: str):
    return s.encode().decode("unicode_escape")

int_decl_parser = string("int").map(lambda _: TypeType.Int)
float_decl_parser = string("float").map(lambda _: TypeType.Float)
char_decl_parser = string("char").map(lambda _: TypeType.Char)
string_decl_parser = string("string").map(lambda _: TypeType.String)
type_parser = int_decl_parser | float_decl_parser | char_decl_parser | string_decl_parser

int_parser = regex(r"-?\d+").map(lambda x: IntLit(int(x)))
string_parser = regex(r'"(?:\\.|[^"\\])*"').map(lambda x: StrLit(unescape(x[1:-1])))
char_parser = regex(r"'.+'").map(lambda x: CharLit(unescape(x[1:-1])))
float_lit = regex(r"-?\d+\.\d+").map(lambda x: FloatLit(float(x)))
lit_parser = float_lit | int_parser | string_parser | char_parser

expr_parser = forward_declaration()

var_ref_parser = identifier.map(Variable)

mult_or_divide_op_parser = ows(string("*") | string("/"))
add_or_subtract_op_parser = ows(string("+") | string("-"))
lt_gt_op_parser = ows(string("<") | string(">"))
eq_op_parser = ows(string("=="))

BinaryOp = Union[Type[Add], Type[Subtract], Type[Multiply], Type[Divide], Type[LessThan], Type[GreaterThan], Type[EqualTo]]
def make_binary_resolver(op1_symbol: str, op1: BinaryOp, op2: BinaryOp):
    def resolver(res: List):
        if len(res[1]) == 0:
            return res[0]

        prev = res[0]
        for next in res[1]:
            if next[0] == op1_symbol:
                prev = op1(prev, next[1])
            else:
                prev = op2(prev, next[1])

        return prev
    return resolver

resolve_mult_expr = make_binary_resolver("*", Multiply, Divide)
resolve_add_expr = make_binary_resolver("+", Add, Subtract)
resolve_lt_gt_expr = make_binary_resolver("<", LessThan, GreaterThan)

def resolve_eq_expr(res: List):
    if len(res[1]) == 0:
        return res[0]

    prev = res[0]
    for next in res[1]:
        prev = EqualTo(prev, next[1])

    return prev

bracketed_expr_parser = seq(
    string('('),
    ows(expr_parser),
    string(')'),
).map(lambda x: x[1])

primary_expr_parser = lit_parser | var_ref_parser |  bracketed_expr_parser

mult_expr_parser = seq(
    primary_expr_parser,
    zero_or_more(seq(mult_or_divide_op_parser, primary_expr_parser))
).map(resolve_mult_expr)


add_expr_parser =  seq(
    mult_expr_parser,
    zero_or_more(seq(add_or_subtract_op_parser, mult_expr_parser))
).map(resolve_add_expr)

lt_gt_expr_parser =  seq(
    add_expr_parser,
    zero_or_more(seq(lt_gt_op_parser, add_expr_parser))
).map(resolve_lt_gt_expr)

expr_parser.become(
    seq(
        lt_gt_expr_parser,
        zero_or_more(seq(eq_op_parser, lt_gt_expr_parser))
    ).map(resolve_eq_expr)
)

command_parser = forward_declaration()

declare_parser = seq(
    type_parser,
    whitespace,
    identifier,
).map(lambda x: Declare(x[0], x[2]))

let_parser = seq(
    identifier,
    ows(string("=")),
    expr_parser
).map(lambda x: Let(x[0], x[2]))

print_parser = (string("print") >> bracketed_expr_parser).map(Print)
input_parser = (
    string("input") >> seq(string("("), identifier, string(")")).map(lambda x: x[1])
).map(Input)

comment_parser = possibly(ows(string("#") >> regex(r"[^\n\r]*")))

@generate
def commands_parser():
    commands = []

    while True:
        command_result = yield possibly(command_parser)
        if len(command_result) == 0:
            break
        commands.append(command_result[0])
        yield (comment_parser >> newline).many()

    return commands

@generate
def if_parser():
    yield string("if") >> whitespace
    if_expr = yield expr_parser
    yield string(":") >> optional_whitespace >> comment_parser >> newline
    parse_state["indent_level"] += 1
    if_commands = yield commands_parser
    assert(len(if_commands) > 0)
    parse_state["indent_level"] -= 1

    return If(if_expr, if_commands)

@generate
def while_parser():
    yield string("while") >> whitespace
    while_expr = yield expr_parser
    yield string(":") >> optional_whitespace >> comment_parser >> newline
    parse_state["indent_level"] += 1
    while_commands = yield commands_parser
    assert(len(while_commands) > 0)
    parse_state["indent_level"] -= 1

    return While(while_expr, while_commands)

command_parser.become(indented(
    if_parser | while_parser | seq(let_parser | declare_parser | print_parser | input_parser, comment_parser) \
    .map(lambda x: x[0])
))

program_parser = seq(
    (ws >> comment_parser).many(),
    commands_parser,
    possibly(ws),
    eof
).map(lambda x: x[1])
