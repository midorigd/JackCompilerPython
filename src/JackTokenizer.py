from src.CompilerResources import TYPE, VALUE, KEYWORD, SYMBOL
from utils.ArrayDeque import ArrayDeque

import re

class Token:
    def __init__(self, type: TYPE, val: VALUE):
        self.type = type
        self.val = val

class JackTokenizer:
    regexTokenPattern = re.compile(r'''
        \d+                         # integer constants
        |
        ".*?"                       # string constants
        |
        [{}()\[\].,;+\-*/&|<>=~]    # symbols
        |
        [a-zA-Z_]\w*                # identifiers
    ''', re.VERBOSE)

    def __init__(self, filename):
        with open(filename) as infile:
            self._data = infile.read()
        self._tokens = ArrayDeque()

        self.tokenizeMap = {
            TYPE.KEYWORD: self.keyword,
            TYPE.SYMBOL: self.symbol,
            TYPE.IDENTIFIER: self.identifier,
            TYPE.INT_CONST: self.intVal,
            TYPE.STRING_CONST: self.stringVal
        }

        self._matchTokens()
        self._tokenize()

    @property
    def _currTokenVal(self):
        return self.currToken.val if isinstance(self.currToken, Token) else self.currToken

    @property
    def nextToken(self) -> Token:
        return self._tokens.first()

    def hasMoreTokens(self):
        return not self._tokens.isEmpty()

    def advance(self) -> Token:
        if not self._tokens.isEmpty():
            self.currToken = self._tokens.dequeueFirst()
            return self.currToken

    def peekSecond(self) -> Token:
        firstToken = self._tokens.dequeueFirst()
        secondToken = self._tokens.first()
        self._tokens.enqueueFirst(firstToken)
        return secondToken

    def _matchTokens(self):
        self._removeComments()
        data = JackTokenizer.regexTokenPattern.findall(self._data)

        for elem in data:
            self._tokens.enqueueLast(elem)

    def _removeComments(self):
        self._data = re.sub(r'/\*.*?\*/', '', self._data, flags=re.DOTALL)
        self._data = re.sub(r'//.*', '', self._data)
    
    def _tokenize(self):
        for i in range(len(self._tokens)):
            tokenVal = self.advance()

            tokenType = self.tokenType()
            tokenVal = self.tokenizeMap[tokenType]()

            token = Token(tokenType, tokenVal)
            self._tokens.enqueueLast(token)

    def tokenType(self) -> TYPE:
        if (token := self._currTokenVal) in KEYWORD:
            return TYPE.KEYWORD
        elif token in SYMBOL:
            return TYPE.SYMBOL
        elif token.isdigit():
            return TYPE.INT_CONST
        elif token.startswith('"'):
            return TYPE.STRING_CONST
        else:
            return TYPE.IDENTIFIER

    def keyword(self) -> KEYWORD:
        if self.tokenType() != TYPE.KEYWORD:
            raise TypeError('Not a keyword token')
        
        return KEYWORD(self._currTokenVal)
    
    def symbol(self) -> SYMBOL:
        if self.tokenType() != TYPE.SYMBOL:
            raise TypeError('Not a symbol token')

        return SYMBOL(self._currTokenVal)
    
    def identifier(self) -> str:
        if self.tokenType() != TYPE.IDENTIFIER:
            raise TypeError('Not an identifier token')
        
        return self._currTokenVal
    
    def intVal(self) -> int:
        if self.tokenType() != TYPE.INT_CONST:
            raise TypeError('Not an integer token')
        
        return int(self._currTokenVal)
    
    def stringVal(self) -> str:
        if self.tokenType() != TYPE.STRING_CONST:
            raise TypeError('Not a string token')
        
        return self._currTokenVal.strip('"')
