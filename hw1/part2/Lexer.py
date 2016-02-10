# """Lexer for SC"""

from collections import deque

class Lexer:
    def __init__(self, srcLoc = 'stdin'):
        self.CurTok = ' '
        self.curStr = '' # empty str
        self.getInpuProg(srcLoc)
    
    def getInpuProg(self, srcLoc):
        if srcLoc == 'stdin':
            print "Please input SC program, press <Ctrl-D> when finish"
            self.__ProgBuffer = deque([]) # List of Strings(Lines)
            while True:
                try:
                    self.__ProgBuffer.append(raw_input())
                except EOFError:
                    self.__ProgBuffer.append('$')
                    break
        else:
            try:
                f = open(srcLoc)
                lines = list(f) # list of lines in file f
                i = 0
                while i < len(lines) - 1: # strip the '\n' in each line except the last line which doesn't end with '\n'
                    lines[i] = lines[i][:-1]
                    i += 1
                self.__ProgBuffer = deque(lines)
                self.__ProgBuffer.append('$')
                f.close()
            except IOError:
                print "[Lexer][Error]: Source file \"%s\" doesn't exist!" % srcLoc
                return
        if __debug__: # testing line diving
            for line in self.__ProgBuffer:
                print line
    
    def getCh(self):
        while self.curStr == '':
            try:
                self.curStr = self.__ProgBuffer.popleft()
            except IndexError:
                print "[Lexer]: Input Processing Finished"
                exit()
        ch = self.curStr[0]
        self.curStr = self.curStr[1:]
        return ch

    def retCh(self, ch): # push back ch that is accidentally ate
        self.curStr = ch + self.curStr

    def getNextToken(self):
        self.CurTok = None
        while self.CurTok is None:
            self.CurTok = self.getTok()
        return self.CurTok

    def getTok(self):
        curCh = ' '
        while curCh.isspace():
            curCh = self.getCh()

        if TokBinOp.isOp(curCh):
            return TokBinOp(curCh)

        if curCh == '=':
            return TokEqual()

        if curCh.isalpha():
            idStr = ''
            while curCh.isalnum() or curCh == '_':
                idStr += curCh
                curCh = self.getCh() # accidentally eat '(' of "if(condition)"
            self.retCh(curCh)
#            if idStr == "if":
#                return TokIf()
#            if idStr == "while":
#                return TokWhile()
            return TokId(idStr)

        if curCh.isdigit() or curCh == '~':
            numStr = ''
            if curCh == '~':
                numStr += '-'
                curCh = self.getCh()
            while curCh.isdigit():
                numStr += curCh
                curCh = self.getCh()# accidentally eat ';' of "a = 10;"
            self.retCh(curCh)
            return TokNum(int(numStr))

        if curCh == '$':
            return TokEOF()

class Tok(object):
    def __init__(self, tokTypeStr = 'empty'):
        self.tokTypeStr = tokTypeStr
    def getTokenName(self):
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

class TokEOF(Tok):
    def __init__(self):
        super(TokEOF, self).__init__(self.__class__.__name__)

# just for testing
if __name__ == '__main__':
    lexer = Lexer('test_input')
    #lexer = Lexer()
    while True:
        lexer.getNextToken()
        print type(lexer.CurTok), lexer.CurTok.getTokenName()

