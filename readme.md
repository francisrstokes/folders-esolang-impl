# Folders

This project explores Folders, a language created by [Daniel Temkin](https://danieltemkin.com/) in 2015.

In Folders, all programs are encoded as deeply nested directories. Names, permissions, and any other aspects are completely ignored - only the structure, patterns, and ordering of the folders is significant.

Here's an [example program](./examples/hi.folderscript) that prints "hi" (note: names are unimportant aside from alphabetical ordering)

```
program
└── a
    ├── a
    │   ├── a
    │   ├── b
    │   ├── c
    │   └── d
    └── b
        ├── a
        │   ├── a
        │   ├── b
        │   ├── c
        │   ├── d
        │   └── e
        ├── b
        │   ├── a
        │   └── b
        └── c
            ├── a
            │   ├── a
            │   │   ├── a
            │   │   ├── b
            │   │   │   └── a
            │   │   ├── c
            │   │   │   └── a
            │   │   └── d
            │   └── b
            │       ├── a
            │       │   └── a
            │       ├── b
            │       ├── c
            │       └── d
            └── b
                ├── a
                │   ├── a
                │   ├── b
                │   │   └── a
                │   ├── c
                │   │   └── a
                │   └── d
                └── b
                    ├── a
                    │   └── a
                    ├── b
                    ├── c
                    └── d
                        └── a
```

## What is this project

This project includes 4 main components:

1. An [unofficial specification document](./docs/spec.md) that builds on the original documentation Daniel put out, but makes decisions to remove some ambiguities
2. A [`parser`](./parser.py), which takes programs written in "folderscript" (a python-like language), and creates a structured representation
3. A [`compiler`](./compiler.py), which take the output of the parser, and encodes a real Folders program on the disk
4. An [`interpreter`](./interpreter.py), which can take a Folders program, and execute it

## Folderscript

The python-like language "Folderscript" allows every operation possible in Folders to be expressed as text. Examples of some Folderscript programs can be found in [the examples](./examples/)

