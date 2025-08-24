# JackCompiler (Python)

This is a Python implementation of the Jack language compiler from projects 10-11 of nand2tetris.

The compiler takes a single `.jack` file or a directory of `.jack` files as a command-line argument and compiles each file into a `.vm` file.

## Modules

JackCompiler: Program entry point

### src

CompilationEngine: Processes tokens and determines compilation routines  
CompilerResources: Enums and tokens for program elements  
JackCompiler: Drives the compilation process  
JackTokenizer: Processes and tokenizes file input  
SymbolTable: Tracks symbol and variable names used in file  
VMWriter: Writes VM commands to output

### utils

ArrayDeque: A simple implementation of a double-ended queue

## Building the project

Run the following from the terminal:

```zsh
git clone https://github.com/midorigd/JackCompilerPython
cd JackCompilerPython
```

## Running the project

Run the following from the project directory:

```zsh
python3 -m JackCompiler <dirname OR filename.jack>
```

## Notes

My C++ implementation of this project: [JackCompiler (C++)](https://github.com/midorigd/JackCompilerCpp)

## References

[nand2tetris](https://www.nand2tetris.org/course)

