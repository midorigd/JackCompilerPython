from src.CompilerResources import SEGMENT, COMMAND

class VMWriter:
    def __init__(self, outfile):
        self.outfile = open(outfile, 'w')

    def writePush(self, segment: SEGMENT, index: int):
        print(f'\tpush {segment.value} {index}', file=self.outfile)

    def writePop(self, segment: SEGMENT, index: int):
        print(f'\tpop {segment.value} {index}', file=self.outfile)

    def writeArithmetic(self, command: COMMAND):
        print(f'\t{command.value}', file=self.outfile)

    def writeLabel(self, label: str):
        print(f'label {label}', file=self.outfile)

    def writeGoto(self, label: str):
        print(f'\tgoto {label}', file=self.outfile)

    def writeIf(self, label: str):
        print(f'\tif-goto {label}', file=self.outfile)

    def writeCall(self, name: str, nArgs: int):
        print(f'\tcall {name} {nArgs}', file=self.outfile)

    def writeFunction(self, name: str, nVars: int):
        print(f'function {name} {nVars}', file=self.outfile)

    def writeReturn(self):
        print('\treturn', file=self.outfile)

    def close(self):
        self.outfile.close()


    def writeConstant(self, index: int):
        self.writePush(SEGMENT.CONST, index)

    def writePushThisPtr(self):
        self.writePush(SEGMENT.POINTER, 0)

    def writePopThisPtr(self):
        self.writePop(SEGMENT.POINTER, 0)

    def writePushThatPtr(self):
        self.writePush(SEGMENT.POINTER, 1)

    def writePopThatPtr(self):
        self.writePop(SEGMENT.POINTER, 1)
