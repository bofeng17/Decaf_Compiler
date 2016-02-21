"""Token definition & action for ply.lex"""

import ply.lex as lex

class DECAFLexer(object):
    def __init__(self, data):
        self.data = data

        # List of token names.
        self.reserved = {
                'boolean': 'BOOLEAN', 'break': 'BREAK', 'continue': 'CONTINUE', 'class': 'CLASS', 'do': 'DO', 'else': 'ELSE',
                'extends': 'EXTENDS', 'false': 'FALSE', 'float': 'FLOAT', 'for': 'FOR', 'if': 'IF', 'int': 'INT',
                'new': 'NEW', 'null': 'NULL', 'private': 'PRIVATE', 'public': 'PUBLIC', 'return': 'RETURN', 'static': 'STATIC',
                'super': 'SUPER', 'this': 'THIS', 'true': 'TRUE', 'void': 'VOID', 'while': 'WHILE',
                }
        self.tokens = ['ID', 'INT_CONST', 'FLOAT_CONST', 'STRING_CONST',
    #              'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
                  'INC', 'DEC',
                  'AND', 'OR',
    #              'NOT', 'ASSN',
                  'EQL', 'UNEQL', 'LE', 'GE',
    #              'LT', 'GT',
    #              'LPAREN', 'RPAREN', 'LBRCKT', 'RBRCKT', 'LBRACE', 'RBRACE',
    #               'COMMA', 'DOT', 'SEMICOL',
                  'comment', 'newline'] + list(self.reserved.values())

        self.literals = "+-*/!=<>()[]{},.;"

        # Regular expression rules for simple tokens
        #t_PLUS    = r'\+' # also UNIADD
        #t_MINUS   = r'-'  # also UNIDED
        #t_TIMES   = r'\*'
        #t_DIVIDE  = r'/'
        self.t_INC     = r'\+\+'
        self.t_DEC     = r'--'
        self.t_AND     = r'&&'
        self.t_OR      = r'\|\|'
        #t_NOT     = r'!'
        #t_ASSN    = r'='
        self.t_EQL     = r'=='
        self.t_UNEQL   = r'!='
        #t_LT      = r'<'
        #t_GT      = r'>'
        self.t_LE      = r'<='
        self.t_GE      = r'>='
        #t_LPAREN  = r'\('
        #t_RPAREN  = r'\)'
        #t_LBRCKT  = r'\['
        #t_RBRCKT  = r'\]'
        #t_LBRACE  = r'\{'
        #t_RBRACE  = r'\}'
        #t_COMMA   = r','
        #t_DOT     = r'\.'
        #t_SEMICOL = r';'
        # be careful handling UNARY Operator {+, -, !}

    # A regular expression rule with some action code
    # t is instance of LexToken.
    # t.type(string), t.value: lexeme(string), t.lineno: current line number, t.lexpos: position of the token relative to the beginning of the input text
    def t_ID(self, t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')    # Check for reserved words
        return t

    def t_FLOAT_CONST(self, t):
        r'\d+(\.\d+)?(e|E)(\+|-)?\d+|\d+\.\d+'
        t.value = float(t.value)
        return t # return whole token

    def t_INT_CONST(self, t):
        r'\d+'
        t.value = int(t.value)
        return t # return whole token

    # Define a rule so we can track line numbers
    # This token doesn't appear in the token list, beacuse it is simply ignored
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)


    # TODO: 1) Strings must be contained within a single line. 2) deal with \n
    def t_STRING_CONST(self, t):
        r'".*"'
        t.value = t.value[1:-1]
        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # TODO: two kinds of comments
    def t_comment(self, t):
        r'//.*|/\*(.|\n)*?\*/'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    
    def scan(self):
#        self.lexer = lex.lex(module = DECAFLexer, debug = 1)
        self.lexer = lex.lex(module = self)

        # Input
        self.lexer.input(self.data)
    
    def test(self):
        # Tokenize
        while True:
            tok = self.lexer.token()
            # sample output: LexToken(tokenName,tokenLexeme,lineNo,colNo)
            print(tok) # if not tok, return None
            if not tok:
                break      # No more input


