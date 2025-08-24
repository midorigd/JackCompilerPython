from src.CompilerResources import SEGMENT, KEYWORD

class SymbolTable:
    class Entry:
        def __init__(self, type: str, segment: SEGMENT, index: int):
            self.type = type
            self.segment = segment
            self.index = index

        def __repr__(self):
            return f'{self.type} {self.segment.value} {self.index}'

    def __init__(self, dumpfile):
        self.data: dict[str, SymbolTable.Entry] = {}
        self.counters = {SEGMENT.THIS: 0, SEGMENT.STATIC: 0, SEGMENT.ARG: 0, SEGMENT.LOCAL: 0}
        self.dumpfile = dumpfile

    def __repr__(self):
        return f'SymbolTable:\n{'\n'.join([f'{name}: {entry}' for name, entry in self.data.items()])}\n------'

    def __contains__(self, name):
        return (name in self.data)

    def reset(self):
        self.data.clear()
        for segment in self.counters:
            self.counters[segment] = 0

    def define(self, name: str, type: str, segment: SEGMENT):
        if segment is SEGMENT.FIELD:
            segment = SEGMENT.THIS

        self.data[name] = SymbolTable.Entry(type, segment, self.counters[segment])
        self.counters[segment] += 1

    def defineThisObject(self, type: str):
        self.define(KEYWORD.THIS, type, SEGMENT.ARG)

    def varCount(self, segment: SEGMENT) -> int:
        if segment is SEGMENT.FIELD:
            segment = SEGMENT.THIS

        return self.counters[segment]

    def getEntry(self, name: str) -> tuple[str, SEGMENT, int]:
        return self.typeOf(name), self.segmentOf(name), self.indexOf(name)

    def typeOf(self, name: str) -> str:
        return self.data[name].type

    def segmentOf(self, name: str) -> SEGMENT:
        return self.data[name].segment

    def indexOf(self, name: str) -> int:
        return self.data[name].index

    def dumpTable(self, tag: str):
        if self.dumpfile is not None:
            with open(self.dumpfile, 'a') as outfile:
                print(tag, self, sep='', file=outfile)
