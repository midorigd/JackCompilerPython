from src.JackCompiler import JackCompiler

import sys

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 -m JackCompiler <dirname OR filename.jack>')
        return

    sourceFile = sys.argv[1]

    compiler = JackCompiler()
    compiler.compile(sourceFile)

main()
