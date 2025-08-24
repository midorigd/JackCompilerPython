from src.JackTokenizer import JackTokenizer, Token
from src.SymbolTable import SymbolTable
from src.VMWriter import VMWriter
from src.CompilerResources import *


class TokenError(Exception):
    '''Next token does not match expected token value or type'''

    def __new__(cls, tokenType: TYPE, tokenVal=VALUE.WILDCARD):
        if tokenVal is VALUE.WILDCARD:
            return super().__new__(WildcardTokenError)
        
        return super().__new__(cls)

    def __init__(self, tokenType: TYPE, tokenVal: VALUE):
        message = f'{tokenType.value} token expected: {tokenVal.value}'
        super().__init__(message)

class WildcardTokenError(TokenError):
    '''Next token does not match expected token type'''

    def __init__(self, tokenType: TYPE, tokenVal: VALUE):
        message = f'Any {tokenType.value} token expected'
        super(Exception, self).__init__(message)

class JackCompilerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)



class CompilationEngine:
    commandLookup = {
        SYMBOL.PLUS: COMMAND.ADD,
        SYMBOL.MINUS: COMMAND.SUB,
        SYMBOL.EQUAL: COMMAND.EQ,
        SYMBOL.GREATER_THAN: COMMAND.GT,
        SYMBOL.LESS_THAN: COMMAND.LT,
        SYMBOL.AMPERSAND: COMMAND.AND,
        SYMBOL.VERTICAL_BAR: COMMAND.OR
    }

    mathLookup = {
        SYMBOL.STAR: 'Math.multiply',
        SYMBOL.SLASH: 'Math.divide'
    }

    def __init__(self, infile: str, outfile: str, dumpfile: str):
        # self.infile = infile
        self._tokenizer = JackTokenizer(infile)
        self.writer = VMWriter(outfile)
        self.labelCount = 0

        self.classSymbolTable = SymbolTable(dumpfile)  # STATIC and FIELD variables
        self.methodSymbolTable = SymbolTable(dumpfile) # ARG and LOCAL variables 

        self.compileClass()

        self.writer.close()

    def getLabel(self):
        val = self.labelCount
        self.labelCount += 1
        return f'L{val}'

    def getLabelPair(self):
        return self.getLabel(), self.getLabel()


    # ADVANCE METHODS

    def advance(self) -> Token:
        return self._tokenizer.advance()

    def guardedAdvance(self, reqType: TYPE, reqVal=VALUE.WILDCARD):
        token = self.advance()

        if not self.compareToken(token, reqType, reqVal):
            raise TokenError(reqType, reqVal)

        return token.val
    
    def compareToken(self, token, reqType: TYPE, reqVal=VALUE.WILDCARD) -> bool:
        if reqVal is VALUE.WILDCARD:
            return token.type is reqType
        else:
            return (token.type, token.val) == (reqType, reqVal)
    
    def compareTokens(self, token, reqsList, *, verbose=False):
        for reqs in reqsList:
            if self.compareToken(token, *reqs):
                return reqs if verbose else True
        
        return False
    
    def nextTokenIs(self, *args):
        return self.compareToken(self._tokenizer.nextToken, *args)
    
    def nextTokenIsOneOf(self, *args):
        return self.compareTokens(self._tokenizer.nextToken, *args)



    # VERIFIER METHODS

    def verifyKeyword(self, *args) -> KEYWORD:
        return self.guardedAdvance(TYPE.KEYWORD, *args)
    
    def verifyIdentifier(self, *args) -> str:
        return self.guardedAdvance(TYPE.IDENTIFIER, *args)
    
    def verifySymbol(self, *args) -> SYMBOL:
        return self.guardedAdvance(TYPE.SYMBOL, *args)
    
    def verifyIntConst(self, *args) -> int:
        return self.guardedAdvance(TYPE.INT_CONST, *args)
    
    def verifyStringConst(self, *args) -> str:
        return self.guardedAdvance(TYPE.STRING_CONST, *args)


    # NON-PRIMITIVE VERIFIER METHODS

    def verifySet(self, reqsList):
        nextToken = self._tokenizer.nextToken

        for reqs in reqsList:
            if self.compareToken(nextToken, *reqs):
                return self.guardedAdvance(*reqs)
        
        raise TokenError(reqsList)

    def verifyVarType(self):
        return self.verifySet(TOKENSET.DATA_TYPES)

    def verifyReturnType(self):
        return self.verifySet(TOKENSET.RETURN_TYPES)


    # NONTERMINAL VERIFIER METHODS

    def isClassVarDec(self):
        return self.nextTokenIsOneOf(TOKENSET.CLASS_VAR_DEC)

    def isSubroutineDec(self):
        return self.nextTokenIsOneOf(TOKENSET.SUBROUTINE_DEC)

    def isVarDec(self):
        return self.nextTokenIs(TYPE.KEYWORD, KEYWORD.VAR)

    def isStatement(self):
        return self.nextTokenIsOneOf(TOKENSET.STATEMENTS)

    def isTerm(self):
        return self.nextTokenIsOneOf(TOKENSET.TERMS, verbose=True)



    # NONTERMINAL COMPILER METHODS
    # EXCLUDED: subroutineCall, subroutineName, varName, className, type, statement

    def compileClass(self):
        # 'class' className '{' classVarDec* subroutineDec* '}'

        self.verifyKeyword(KEYWORD.CLASS)
        self.className = self._compileName()
        self.verifySymbol(SYMBOL.CURL_L)

        while self.isClassVarDec():
            self.compileClassVarDec()

        while self.isSubroutineDec():
            self.compileSubroutine()

        self.verifySymbol(SYMBOL.CURL_R)

        self.classSymbolTable.dumpTable(f'{self.className} class')

    def compileClassVarDec(self):
        # ('static' | 'field') type varName ( ',' varName )* ';'

        symbolSegment = self.verifyKeyword()
        symbolType = self.verifyVarType()

        while True:
            symbolName = self._compileVarName(isDeclaration=True, classScope=True, type=symbolType, segment=SEGMENT(symbolSegment.value))

            if not self.nextTokenIs(TYPE.SYMBOL, SYMBOL.COMMA):
                break

            self.verifySymbol(SYMBOL.COMMA)

        self.verifySymbol(SYMBOL.SEMICOLON)

    def compileSubroutine(self):
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody

        # constructor:  push # field vars, alloc, then pop address to this ptr
        # method:       pop address of this/self (first arg) to this ptr
        # function:     no extra args

        subroutineType = self.verifyKeyword()
        self.verifyReturnType()
        subroutineName = self._compileName()

        self.methodSymbolTable.reset()

        if subroutineType is KEYWORD.METHOD:
            self.methodSymbolTable.defineThisObject(self.className)

        self.verifySymbol(SYMBOL.PAREN_L)
        self.compileParameterList()
        self.verifySymbol(SYMBOL.PAREN_R)

        self.compileSubroutineBody(subroutineName, subroutineType)

        self.methodSymbolTable.dumpTable(f'{subroutineName} method')

    def compileParameterList(self):
        # ( ( type varName ) ( ',' type varName )* )?

        if self.nextTokenIs(TYPE.SYMBOL, SYMBOL.PAREN_R):
            return

        while True:
            symbolType = self.verifyVarType()
            symbolName = self._compileVarName(isDeclaration=True, type=symbolType, segment=SEGMENT.ARG)

            if not self.nextTokenIs(TYPE.SYMBOL, SYMBOL.COMMA):
                break

            self.verifySymbol(SYMBOL.COMMA)

    def compileSubroutineBody(self, name, type):
        # '{' varDec* statements '}'

        self.verifySymbol(SYMBOL.CURL_L)

        while self.isVarDec():
            self.compileVarDec()

        self._compileFunctionHeader(name, type)

        self.compileStatements()
        self.verifySymbol(SYMBOL.CURL_R)

    def compileVarDec(self):
        # 'var' type varName ( ',' varName )* ';'

        self.verifyKeyword(KEYWORD.VAR)
        symbolType = self.verifyVarType()

        while True:
            symbolName = self._compileVarName(isDeclaration=True, type=symbolType, segment=SEGMENT.LOCAL)

            if not self.nextTokenIs(TYPE.SYMBOL, SYMBOL.COMMA):
                break

            self.verifySymbol(SYMBOL.COMMA)

        self.verifySymbol(SYMBOL.SEMICOLON)


    def _compileFunctionHeader(self, name, type):
        functionName = f'{self.className}.{name}'
        nVars = self.methodSymbolTable.varCount(SEGMENT.LOCAL)
        self.writer.writeFunction(functionName, nVars)

        if type is KEYWORD.CONSTRUCTOR:
            nFields = self.classSymbolTable.varCount(SEGMENT.THIS)
            self.writer.writeConstant(nFields)
            self.writer.writeCall('Memory.alloc', 1)
            self.writer.writePopThisPtr()

        elif type is KEYWORD.METHOD:
            thisSegment = self.methodSymbolTable.segmentOf(KEYWORD.THIS)
            thisIndex = self.methodSymbolTable.indexOf(KEYWORD.THIS)
            self.writer.writePush(thisSegment, thisIndex)
            self.writer.writePopThisPtr()


    def _isVarName(self, name):
        if name in self.methodSymbolTable:
            return self.methodSymbolTable

        elif name in self.classSymbolTable:
            return self.classSymbolTable

        return None

    def _compileVarName(self, *, isDeclaration=False, **kwargs):
        if not self.nextTokenIs(TYPE.IDENTIFIER):
            raise TokenError(TYPE.IDENTIFIER)

        token = self._tokenizer.advance()
        varName = token.val

        if isDeclaration:
            self._compileSymbolDec(varName, **kwargs)
            return varName
        else:
            return self._compileSymbolUse(varName)

    def _compileSymbolDec(self, name: str, type: str, segment: SEGMENT, classScope=False):
        currSymbolTable = self.classSymbolTable if classScope else self.methodSymbolTable
        currSymbolTable.define(name, type, segment)

    def _compileSymbolUse(self, name: str):
        if not (currSymbolTable := self._isVarName(name)):
            raise JackCompilerError(f'Undefined symbol: {name}')

        return currSymbolTable.getEntry(name)

    def _compileName(self):
        if not self.nextTokenIs(TYPE.IDENTIFIER):
            raise TokenError(TYPE.IDENTIFIER)

        token = self._tokenizer.advance()
        name = token.val

        return name


    def _compileSubroutineCall(self):
        #                             subroutineName '(' expressionList ')' |
        # ( className | varName ) '.' subroutineName '(' expressionList ')'

        # internal method (no dot):        className is current class:   push this to stack as first arg
        # external method (varName):       className is type(varName):   push var to stack as first arg
        # external function (className):   className is provided:        done??

        className = self.className
        nArgs = 1

        if self.compareToken(self._tokenizer.peekSecond(), TYPE.SYMBOL, SYMBOL.DOT):
            symbolName = self._tokenizer.nextToken.val

            if self._isVarName(symbolName):
                type, segment, index = self._compileVarName()
                self.writer.writePush(segment, index)
                className = type

            else:
                className = self._compileName()
                nArgs = 0

            self.verifySymbol(SYMBOL.DOT)

        else:
            self.writer.writePushThisPtr()

        subroutineName = self._compileName()

        self.verifySymbol(SYMBOL.PAREN_L)
        nArgs += self.compileExpressionList()
        self.verifySymbol(SYMBOL.PAREN_R)

        functionName = f'{className}.{subroutineName}'
        self.writer.writeCall(functionName, nArgs)



    def compileStatements(self):
        # ( letStatement | ifStatement | whileStatement | doStatement | returnStatement )*

        self.statementMap = {
            KEYWORD.LET: self.compileLet,
            KEYWORD.IF: self.compileIf,
            KEYWORD.WHILE: self.compileWhile,
            KEYWORD.DO: self.compileDo,
            KEYWORD.RETURN: self.compileReturn
        }

        while self.isStatement():
            self.statementMap[self._tokenizer.nextToken.val]()

    def compileLet(self):
        # 'let' varName ( '[' expression ']' )? '=' expression ';'

        self.verifyKeyword(KEYWORD.LET)
        _, segment, index = self._compileVarName()

        if self.nextTokenIs(TYPE.SYMBOL, SYMBOL.SQUARE_L):
            self.writer.writePush(segment, index)

            self.verifySymbol(SYMBOL.SQUARE_L)
            self.compileExpression()
            self.verifySymbol(SYMBOL.SQUARE_R)

            self.writer.writeArithmetic(COMMAND.ADD)

            self.verifySymbol(SYMBOL.EQUAL)
            self.compileExpression()
            self.verifySymbol(SYMBOL.SEMICOLON)

            self.writer.writePop(SEGMENT.TEMP, 0)
            self.writer.writePopThatPtr()
            self.writer.writePush(SEGMENT.TEMP, 0)
            self.writer.writePop(SEGMENT.THAT, 0)

        else:
            self.verifySymbol(SYMBOL.EQUAL)
            self.compileExpression()
            self.verifySymbol(SYMBOL.SEMICOLON)

            self.writer.writePop(segment, index)

    def compileIf(self):
        # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?

        ifLabel, gotoLabel = self.getLabelPair()

        self.verifyKeyword(KEYWORD.IF)
        self.verifySymbol(SYMBOL.PAREN_L)
        self.compileExpression()
        self.verifySymbol(SYMBOL.PAREN_R)

        self.writer.writeArithmetic(COMMAND.NOT)
        self.writer.writeIf(ifLabel)

        self.verifySymbol(SYMBOL.CURL_L)
        self.compileStatements()
        self.verifySymbol(SYMBOL.CURL_R)

        self.writer.writeGoto(gotoLabel)
        self.writer.writeLabel(ifLabel)

        if self.nextTokenIs(TYPE.KEYWORD, KEYWORD.ELSE):
            self.verifyKeyword(KEYWORD.ELSE)
            self.verifySymbol(SYMBOL.CURL_L)
            self.compileStatements()
            self.verifySymbol(SYMBOL.CURL_R)

        self.writer.writeLabel(gotoLabel)

    def compileWhile(self):
        # 'while' '(' expression ')' '{' statements '}'

        loopLabel, exitLabel = self.getLabelPair()

        self.verifyKeyword(KEYWORD.WHILE)

        self.writer.writeLabel(loopLabel)

        self.verifySymbol(SYMBOL.PAREN_L)
        self.compileExpression()
        self.verifySymbol(SYMBOL.PAREN_R)

        self.writer.writeArithmetic(COMMAND.NOT)
        self.writer.writeIf(exitLabel)

        self.verifySymbol(SYMBOL.CURL_L)
        self.compileStatements()
        self.verifySymbol(SYMBOL.CURL_R)

        self.writer.writeGoto(loopLabel)
        self.writer.writeLabel(exitLabel)

    def compileDo(self):
        # 'do' subroutineCall ';'

        self.verifyKeyword(KEYWORD.DO)
        self._compileSubroutineCall()
        self.verifySymbol(SYMBOL.SEMICOLON)

        self.writer.writePop(SEGMENT.TEMP, 0)

    def compileReturn(self):
        # 'return' expression? ';'

        self.verifyKeyword(KEYWORD.RETURN)

        if self.nextTokenIs(TYPE.SYMBOL, SYMBOL.SEMICOLON):
            self.writer.writeConstant(0) # dummy value
        else:
            self.compileExpression()

        self.verifySymbol(SYMBOL.SEMICOLON)

        self.writer.writeReturn()


    def compileExpression(self):
        # term ( op term )*

        self.compileTerm()

        while self.nextTokenIsOneOf(TOKENSET.OPERATORS):
            op = self.verifySymbol()
            self.compileTerm()

            if op in CompilationEngine.commandLookup:
                self.writer.writeArithmetic(CompilationEngine.commandLookup[op])
            else:
                self.writer.writeCall(CompilationEngine.mathLookup[op], 2)

    def compileTerm(self):
        # intConst | stringConst | keywordConst | varName | varName '[' expression ']'
        # | subroutineCall | '(' expression ')' | unaryOp term

        def isSubroutineCall(token):
            return self.compareTokens(token, TOKENSET.SUBROUTINE_CALL)

        if self.nextTokenIs(TYPE.INT_CONST):
            val = self.verifyIntConst()
            self.writer.writeConstant(val)

        elif self.nextTokenIs(TYPE.STRING_CONST):
            string = self.verifyStringConst()

            self.writer.writeConstant(len(string))
            self.writer.writeCall('String.new', 1)
            for char in string:
                self.writer.writeConstant(ord(char))
                self.writer.writeCall('String.appendChar', 2)
            self.writer.writePush

        elif self.nextTokenIsOneOf(TOKENSET.KEYWORD_CONSTANTS):
            self._compileKeywordConst()

        elif self.nextTokenIs(TYPE.IDENTIFIER):
            if self.compareToken((secondToken := self._tokenizer.peekSecond()), TYPE.SYMBOL, SYMBOL.SQUARE_L):
                _, segment, index = self._compileVarName()
                self.writer.writePush(segment, index)

                self.verifySymbol(SYMBOL.SQUARE_L)
                self.compileExpression()
                self.verifySymbol(SYMBOL.SQUARE_R)

                self.writer.writeArithmetic(COMMAND.ADD)
                self.writer.writePopThatPtr()
                self.writer.writePush(SEGMENT.THAT, 0)

            elif isSubroutineCall(secondToken):
                self._compileSubroutineCall()

            else:
                _, segment, index = self._compileVarName()
                self.writer.writePush(segment, index)

        elif self.nextTokenIs(TYPE.SYMBOL, SYMBOL.PAREN_L):
            self.verifySymbol(SYMBOL.PAREN_L)
            self.compileExpression()
            self.verifySymbol(SYMBOL.PAREN_R)

        elif self.nextTokenIsOneOf(TOKENSET.UNARY_OPS):
            op = COMMAND.NEG if self.verifySymbol() is SYMBOL.MINUS else COMMAND.NOT
            self.compileTerm()
            self.writer.writeArithmetic(op)

        else:
            raise TokenError(NONTERMINAL.TERM)

    def compileExpressionList(self) -> int:
        # ( expression ( ',' expression )* )?

        count = 0

        if not self.nextTokenIs(TYPE.SYMBOL, SYMBOL.PAREN_R):
            self.compileExpression()
            count += 1

            while self.nextTokenIs(TYPE.SYMBOL, SYMBOL.COMMA):
                self.verifySymbol(SYMBOL.COMMA)
                self.compileExpression()
                count += 1

        return count


    def _compileKeywordConst(self):
        # 'true' | 'false' | 'null' | 'this'

        if (constant := self.verifyKeyword()) is KEYWORD.TRUE:
            self.writer.writeConstant(1)
            self.writer.writeArithmetic(COMMAND.NEG)

        elif constant is KEYWORD.THIS:
            self.writer.writePushThisPtr()

        else:
            self.writer.writeConstant(0)
