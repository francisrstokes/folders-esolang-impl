# Folders Esolang Spec (unofficial)

Folders is a language created by [Daniel Temkin](https://danieltemkin.com/) in 2015.

All programs are expressed solely as an ordered tree of folders. Aside from an explicit alphabetical ordering, the name of any given folder is insignificant.

Programs are made up of commands like declaring and assigning variables, getting user input, printing to the screen, performing loops, and taking conditional actions. Expressions (things which evaluate to a concrete value) can have 4 types: integer, floating point number, string, and char. Expression types include literal values, variable references, arithmetic operations (add/subtract/multiply/divide), and comparisons (equal to/less than/greater than).

The [esolangs wiki page](https://esolangs.org/wiki/Folders) does not specify many aspects of the language explicitly. This is, of course, not actually a problem at all, since this language is not intended to be general purpose. However it does make it difficult to write a "correct" implementation. Daniel's reference implementation is the only example point, and it being a C#.NET project from 10+ years ago makes it quite difficult to get compiled and running on my linux machine.

This document attempts to act as a spec for my own implementation, concretely detailing ambiguous elements. As an example, this document and implementation make decisions about:

- Endianness
- Bit ordering
- Types of expressions
- Strictness of types
- Integer width and signedness

## Program

- A *program* is a folder whose subfolders are all *commands*

## Command

- A *command* is a folder whose subfolders dictate the type of the command.
- A *command* has 2 or 3 subfolders
- The number of folders within the first subfolder always encode the *command type*
- The second and third subfolders encode *command type*-specific information, which may be a sequence of commands, or an *expression*

### Command Types

| Command | # of folders | Second subfolder | Third subfolder    |
| ------- | ------------ | ---------------- | ------------------ |
| if      | 0            | *Expression*     | *List of commands* |
| while   | 1            | *Expression*     | *List of commands* |
| declare | 2            | *Value type*     | *String* (name)    |
| let     | 3            | *String* (name)  | *Expression*       |
| print   | 4            | *Expression*     | Not applicable     |
| input   | 5            | *String* (name)  | Not applicable     |

## Expression

- An *expression* is a folder whose subfolders dictate the type of the expression
- An *expression* has 2 or 3 subfolders
- The number of folders within the first subfolder always encode the *expression type*
- The second and third subfolders encode *expression type*-specific  information, which may be themselves *expressions*, *value types*, or *strings* (referencing a variable)

### Expression Types

| Expression    | # of folders | Second subfolder   | Third subfolder    |
| ------------- | ------------ | ------------------ | ------------------ |
| Variable      | 0            | *String* (name)    | Not applicable     |
| Add           | 1            | *Expression* (lhs) | *Expression* (rhs) |
| Subtract      | 2            | *Expression* (lhs) | *Expression* (rhs) |
| Multiply      | 3            | *Expression* (lhs) | *Expression* (rhs) |
| Divide        | 4            | *Expression* (lhs) | *Expression* (rhs) |
| Literal Value | 5            | *Value type*       | *Encoded value*    |
| Equal To      | 5            | *Expression* (lhs) | *Expression* (rhs) |
| Greater Than  | 5            | *Expression* (lhs) | *Expression* (rhs) |
| Less Than     | 5            | *Expression* (lhs) | *Expression* (rhs) |

## Value Type

- A *value type* is a number of subfolders that encode one of the 4 possible value types
- *Value types* are used in *Literal value expressions*, and in the *Declare command*

| Type          | # of folders |
| ------------- | ------------ |
| int           | 0            |
| float         | 1            |
| string        | 2            |
| char          | 3            |

## Literal Values

- All literal values in the folders language are expressed using *nibbles*
- How the *nibbles* are grouped to form larger values differs per type
- At all applicable scales (nibble, byte, multi-byte), data is arrange most significant to least significant

### Nibble

- A *nibble* is a folder with exactly four subfolders
- Each of the subfolders represents 1 bit of a 4 bit value
    - The first subfolder in the nibble represents the most significant bit, and the fourth subfolder represents the least significant bit
    - The existence of a subfolder inside the bit subfolder signifies a `1`
    - The absence of a subfolder inside the bit subfolder signifies a `0`

### Int

- The `int` type is a twos-complement signed 32-bit integer, with wraparound on overflow and underflow
- An *int literal* is a folder with exactly 8 subfolders, each of which is a *nibble*
- The first *nibble* represents the most significant 4 bits of the integer, and each successive *nibble* represent the next successive 4 bits

### Float

- The `float` type is a 32-bit single precision IEEE-754 floating point number
- A *float literal* is a folder with exactly 8 subfolders, each of which is a *nibble*
- The first *nibble* represents the most significant 4 bits of the integer, and each successive *nibble* represent the next successive 4 bits

### String

- The `string` type is a UTF-8 encoded string
- A *string literal* is a folder whose subfolders are an ordered set of *bytes*
- A *byte* is a folder with exactly 2 subfolders, each of which is a nibble
    - The first *nibble* in a byte is the most significant 4 bits, and the second *nibble* is the least significant 4 bits

### Char

- The `char` type is an unsigned 8-bit integer (`uint32_t`), with wraparound on overflow and underflow
- A *char literal* is a folder whose subfolders with exactly 2 subfolders, each of which is a nibble
- The first *nibble* is the most significant 4 bits, and the second *nibble* is the least significant 4 bits

## Types of expressions and strictness

- Every *expression* has a derived type
- In the `Add` *expression*:
    - The left and right hand side **may** be of different types only when the left hand side is a *string* and the right hand side is a *char*. The type of the expression is then a *string*
    - The left and right hand side **must otherwise** be the same type, and the type of the expression will also be this type
- In the `Subtract` *expression*:
    - The left and right hand side **must** be the same type, and the type of the expression will also be this type
    - The left and right hand type may be *int*, *float*, or *char*
- In the `Multiply` *expression*:
    - The left and right hand side **must** be the same type, and the type of the expression will also be this type
    - The left and right hand type may be *int*, *float*, or *char*
- In the `Divide` *expression*:
    - The left and right hand side **must** be the same type, and the type of the expression will also be this type
    - The left and right hand type may be *int*, *float*, or *char*
- The following combinations are valid when comparing different types using `Equal To`, `Less Than`, and `Greater Than`:

|          | `int` | `float` | `string` | `char` |
|:--------:|:-----:|:-------:|:--------:|:------:|
| `int`    | ✅    | ✅      | ❌       | ✅     |
| `float`  | ✅    | ✅      | ❌       | ✅     |
| `string` | ❌    | ❌      | ✅       | ✅     |
| `char`   | ✅    | ✅      | ✅       | ✅     |

- When comparing a `char` to an `int` or `float`, the `char` value is compared numerically using its value between 0 and 255

## Appendix: Type-based grammar

The following is a TypeScript-ish type-level representation of the structure of a folders program.

```typescript
type Program      = Command[];

type Command      = If | While | Declare | Let | Print | Input;
enum CommandType {
    If            = 0,
    While         = 1,
    Declare       = 2,
    Let           = 3,
    Print         = 4,
    Input         = 5
}

type ValueType = int | float | string | char;
enum LiteralType {
    Int           = 0,
    Float         = 1,
    String        = 2,
    Char          = 3
}

type If           = { tag: CommandType.If;      expr: Expression;  commands: Command[];                        }
type While        = { tag: CommandType.While;   expr: Expression;  commands: Command[];                        }
type Declare      = { tag: CommandType.Declare; type: LiteralType; name: string;                               }
type Let          = { tag: CommandType.Let;     name: string;      expr: Expression;                           }
type Print        = { tag: CommandType.Print;   expr: Expression;                                              }
type Input        = { tag: CommandType.Input;   name: string;                                                  }

type Expression   = Variable | Add | Subtract | Multiply | Divide | LiteralValue | EqualTo | GreaterThan | LessThan;
enum ExpressionType {
    Variable      = 0,
    Add           = 1,
    Subtract      = 2,
    Multiply      = 3,
    Divide        = 4,
    LiteralValue  = 5,
    EqualTo       = 6,
    GreaterThan   = 7,
    LessThan      = 8
}

type Variable     = { tag: ExpressionType.Variable;     name: string;                                          }
type Add          = { tag: ExpressionType.Add;          lhs: Expression;   rhs: Expression;                    }
type Subtract     = { tag: ExpressionType.Subtract;     lhs: Expression;   rhs: Expression;                    }
type Multiply     = { tag: ExpressionType.Multiply;     lhs: Expression;   rhs: Expression;                    }
type Divide       = { tag: ExpressionType.Divide;       lhs: Expression;   rhs: Expression;                    }
type LiteralValue = { tag: ExpressionType.LiteralValue; tag: LiteralType;  value: ValueType;                   }
type EqualTo      = { tag: ExpressionType.EqualTo;      lhs: Expression;   rhs: Expression;                    }
type GreaterThan  = { tag: ExpressionType.GreaterThan;  lhs: Expression;   rhs: Expression;                    }
type LessThan     = { tag: ExpressionType.LessThan;     lhs: Expression;   rhs: Expression;                    }
```
