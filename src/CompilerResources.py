# These tags are defined so they can be used in place of literals when matching token types, keyword types, etc.

from enum import Enum


class TYPE(Enum):
    KEYWORD = 'keyword'
    SYMBOL = 'symbol'
    INT_CONST = 'integerConstant'
    STRING_CONST = 'stringConstant'
    IDENTIFIER = 'identifier'

class VALUE:
    @classmethod
    def members(cls):
        return cls._value2member_map_.keys()

    WILDCARD = None

class KEYWORD(VALUE, Enum):
    # Directives and classifiers
    CLASS = 'class'
    CONSTRUCTOR = 'constructor'
    FUNCTION = 'function'
    METHOD = 'method'
    FIELD = 'field'
    STATIC = 'static'
    VAR = 'var'

    # Data types
    INT = 'int'
    CHAR = 'char'
    BOOLEAN = 'boolean'
    VOID = 'void'

    # Values
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'
    THIS = 'this'

    # Flow control structures
    LET = 'let'
    DO = 'do'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    RETURN = 'return'

class SYMBOL(VALUE, Enum):
    CURL_L = '{'
    CURL_R = '}'
    PAREN_L = '('
    PAREN_R = ')'
    SQUARE_L = '['
    SQUARE_R = ']'
    DOT = '.'
    COMMA = ','
    SEMICOLON = ';'
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    SLASH = '/'
    AMPERSAND = '&'
    VERTICAL_BAR = '|'
    LESS_THAN = '<'
    GREATER_THAN = '>'
    EQUAL = '='
    SQUIGGLE = '~'


class NONTERMINAL:
    CLASS = 'class'
    CLASS_VAR_DEC = 'classVarDec'
    SUBROUTINE_DEC = 'subroutineDec'
    PARAMETER_LIST = 'parameterList'
    SUBROUTINE_BODY = 'subroutineBody'
    SUBROUTINE_CALL = 'subroutineCall'
    VAR_DEC = 'varDec'
    STATEMENTS = 'statements'
    LET = 'letStatement'
    IF = 'ifStatement'
    WHILE = 'whileStatement'
    DO = 'doStatement'
    RETURN = 'returnStatement'
    EXPRESSION = 'expression'
    TERM = 'term'
    EXPRESSION_LIST = 'expressionList'


class SEGMENT(Enum):
    # symbol segments
    FIELD = 'field'
    THIS = 'this'
    STATIC = 'static'
    ARG = 'argument'
    LOCAL = 'local'

    CONST = 'constant'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'

class COMMAND(Enum):
    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    AND = 'and'
    OR = 'or'
    NOT = 'not'


class TOKENSET:
    DATA_TYPES = {
        (TYPE.KEYWORD, KEYWORD.INT),
        (TYPE.KEYWORD, KEYWORD.CHAR),
        (TYPE.KEYWORD, KEYWORD.BOOLEAN),
        (TYPE.IDENTIFIER, )
    }

    RETURN_TYPES = { (TYPE.KEYWORD, KEYWORD.VOID) } | DATA_TYPES

    CLASS_VAR_DEC = {
        (TYPE.KEYWORD, KEYWORD.STATIC),
        (TYPE.KEYWORD, KEYWORD.FIELD)
    }

    SUBROUTINE_DEC = {
        (TYPE.KEYWORD, KEYWORD.CONSTRUCTOR),
        (TYPE.KEYWORD, KEYWORD.FUNCTION),
        (TYPE.KEYWORD, KEYWORD.METHOD)
    }

    STATEMENTS = {
        (TYPE.KEYWORD, KEYWORD.LET),
        (TYPE.KEYWORD, KEYWORD.IF),
        (TYPE.KEYWORD, KEYWORD.WHILE),
        (TYPE.KEYWORD, KEYWORD.DO),
        (TYPE.KEYWORD, KEYWORD.RETURN)
    }

    UNARY_OPS = {
        (TYPE.SYMBOL, SYMBOL.MINUS),
        (TYPE.SYMBOL, SYMBOL.SQUIGGLE)
    }

    OPERATORS = {
        (TYPE.SYMBOL, SYMBOL.PLUS),
        (TYPE.SYMBOL, SYMBOL.MINUS),
        (TYPE.SYMBOL, SYMBOL.STAR),
        (TYPE.SYMBOL, SYMBOL.SLASH),
        (TYPE.SYMBOL, SYMBOL.AMPERSAND),
        (TYPE.SYMBOL, SYMBOL.VERTICAL_BAR),
        (TYPE.SYMBOL, SYMBOL.LESS_THAN),
        (TYPE.SYMBOL, SYMBOL.GREATER_THAN),
        (TYPE.SYMBOL, SYMBOL.EQUAL)
    }

    KEYWORD_CONSTANTS = {
        (TYPE.KEYWORD, KEYWORD.TRUE),
        (TYPE.KEYWORD, KEYWORD.FALSE),
        (TYPE.KEYWORD, KEYWORD.NULL),
        (TYPE.KEYWORD, KEYWORD.THIS)
    }

    TERMS = {
        (TYPE.INT_CONST, ),
        (TYPE.STRING_CONST, ),
        (TYPE.IDENTIFIER, ),
        (TYPE.SYMBOL, SYMBOL.PAREN_L),
    } | KEYWORD_CONSTANTS | UNARY_OPS

    SUBROUTINE_CALL = {
        (TYPE.SYMBOL, SYMBOL.PAREN_L),
        (TYPE.SYMBOL, SYMBOL.DOT)
    }
