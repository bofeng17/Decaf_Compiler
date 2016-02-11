# """Toke Definition for SC"""

class Tok(object):
    def __init__(self, tokTypeStr = 'empty'):
        self.tokTypeStr = tokTypeStr
    def getTokName(self):
        return self.tokTypeStr

class TokBinOp(Tok):
    precd = {'+':20, '-':20, '*':40, '/':40, '%':40}
    assoc = {'+':0, '-':0, '*':0, '/':0, '%':0} # 0 for left associativity, 1 for right
    opSet = set('+-*/%')

    def __init__(self, op):
        self.op = op
        super(TokBinOp, self).__init__(self.__class__.__name__)

    @staticmethod
    def isOp(op):
        return op in TokBinOp.opSet

    def getOp(self):
        return self.op

    def getPrecedence(self):
        return TokBinOp.precd[self.op]

    def ifLeftAssociativity(self):
        return TokBinOp.assoc[self.op]

class TokEqual(Tok):
    def __init__(self):
        super(TokEqual, self).__init__(self.__class__.__name__)

class TokId(Tok):
    def __init__(self, idStr):
        self.idStr = idStr
        super(TokId, self).__init__(self.__class__.__name__)
    def getIdStr(self):
        return self.idStr

class TokNum(Tok):
    def __init__(self, numVal):
        self.numVal = numVal
        super(TokNum, self).__init__(self.__class__.__name__)
    def getNumVal(self):
        return self.numVal

class TokTerm(Tok):
    def __init__(self):
        super(TokTerm, self).__init__(self.__class__.__name__)

class TokEOF(Tok):
    def __init__(self):
        super(TokEOF, self).__init__(self.__class__.__name__)

