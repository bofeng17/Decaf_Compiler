from AST import AssignStmtAST, IdentiferAST, ConstantAST, BinOpExprAST

class Parser():
    """Parser class for SC, each call to parse() return a constructed AST"""
    def __init__(self, lexer):
        self.__curr_lexer = lexer
    def lexerMoveOn(self):
        self.__curr_lexer.getNextToken()
    def tokenIs(self, tok):#tok is string type
        return tok == self.__curr_lexer.CurTok.getTokName()
    #will move forward current token if assertion passed
    def tokenShouldBe(self, expect_tok):#expect_tok is string type
        assert self.tokenIs(expect_tok), "error: expect token: %r" %expect_tok
        self.lexerMoveOn()

    #Note: after call to parseExpr(), Curtok will point to the next token that needs to be processed
    def parseExpr(self):
        if self.tokenIs('TokNum'):
            expr_ast = ConstantAST(self.__curr_lexer.CurTok.getNumVal())
            self.lexerMoveOn()
        elif self.tokenIs('TokId'):#TODO: check if at code emit stage will check sym initialized
            expr_ast = IdentiferAST(self.__curr_lexer.CurTok.getIdStr())
            self.lexerMoveOn()
        elif self.tokenIs('TokBinOp'):
            op = self.__curr_lexer.CurTok.getOp()
            self.lexerMoveOn()
            lnode_ast = self.parseExpr()
            rnode_ast = self.parseExpr()
            expr_ast = BinOpExprAST(op, lnode_ast, rnode_ast)
        else:
            assert False, "error: token [%r] is not expected in Expression"%self.__curr_lexer.CurTok.getTokName()

        return expr_ast


    #Note: after call to parseStmt(), Curtok will point to the next token that needs to be processed
    def parseStmt(self):
        if self.tokenIs('TokId'):
            idenAST = IdentiferAST(self.__curr_lexer.CurTok.getIdStr())
            self.lexerMoveOn()#eat idTok
            self.tokenShouldBe('TokEqual')
            exprAST = self.parseExpr()
            self.tokenShouldBe('TokTerm')
            return AssignStmtAST(idenAST, exprAST)
        else:
            assert False, "error: expect first token at a stmt to be TokId"
    def parse(self):
        ast = self.parseStmt()
        return ast
