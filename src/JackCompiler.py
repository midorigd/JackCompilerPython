from src.CompilationEngine import CompilationEngine

import glob

class JackCompiler:
    def __init__(self):
        pass

    def compile(self, sourceFile: str, *, debugFile=None):
        if sourceFile.endswith('.jack'):
            files = [sourceFile]
        else:
            files = glob.glob(f'{sourceFile}/*.jack')

        for infile in files:
            outfile = f'{infile.strip('.jack')}.vm'
            self.compileFile(infile, outfile, debugFile)

    def compileFile(self, infile: str, outfile: str, debugFile: str):
        CompilationEngine(infile, outfile, debugFile)
