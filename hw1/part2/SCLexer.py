# """Lexer for SC"""

import re
from collections import deque

class Lexer:
    def __init__(self, srcLoc = 'stdin'):
        self.CurTok = ' '
        self.getInpuProg(srcLoc)
    
    def getInpuProg(self, srcLoc):
        self.__ProgBuffer = deque([]) # List of Strings(Lines)
        print "Please input SC program, press <Ctrl-D> when finish"
        while True:
            try:
                if srcLoc == 'stdin':
                    self.__ProgBuffer.append(raw_input())
                else:
                    f = open(srcLoc)
                    self.__ProgBuffer.append(f.readline())
            except EOFError:
                self.__ProgBuffer.append('$')
                break
    
    def getCh(self):
        try:
            curStr = self.__ProgBuffer.popleft()
            for ch in curStr:
                if ord(ch) != 0xA:
                    return ch # be cautious for 0xA Line Feed and Another Whitespace
        except IndexError:
            print "Input Processing Finished"
            exit()

    def getNextToken(self):
        self.CurTok = self.getTok()
        return self.CurTok

    def getTok(self):
        curChar = ' '
        while curChar.isspace():
            curChar = sys.stdin.read(1)

        if curChar.isalpha():
            idStr = ''
            while curChar.isalnum() or curChar == '_':
                idStr += curChar
                curChar = sys.stdin.read(1) # Bug: accidentally eat '(' of "if(condition)"
#            if idStr == "if":
#                return TokIf()
#            if idStr == "while":
#                return TokWhile()
            return TokId(idStr)

        if curChar.isdigit() or curChar == '~':
            numStr = ''
            if curChar == '~':
                numStr += '-'
                curChar = sys.stdin.read(1)
            while curChar.isdigit():
                numStr += curChar
                curChar = sys.stdin.read(1)# Bug: accidentally eat ';' of "a = 10;"
            return TokConst(int(numStr))

        if curChar == '$':
            return TokEOF()

class Tok:
    def __init__(self):
        self.tokTypeStr = ''
    def getTokenName(self):
        return self.tokTypeStr

class TokBinOp(Tok):
    precd = {'+':20, '-':20, '*':40, '/':40, '%':40}
    assoc = {'+':0, '-':0, '*':0, '/':0, '%':0} # 0 for left associativity, 1 for right
    opSet = set('+-*/%')

    def __init__(self, op):
        self.op = op
        self.tokTypeStr = self.__class__.__name__

    @staticmethod
    def isOp(op):
        return op in TokBinOp.opSet

    def getOp(self):
        return self.op

    def getPrecedence(self):
        return TokBinOp.precd[self.op]

    def ifLeftAssociativity(self):
        return TokBinOp.assoc[self.op]

class TokId:
    def __init__(self, idStr):
        self.idStr = idStr
        self.name = 'TokId'
    def getIdStr(self):
        return self.idStr
    def getTokName(self):
        return self.name


class TokNum:
    def __init__(self, numVal):
        self.numVal = numVal
    def getNumVal(self):
        return self.numVal

class TokEOF:
    def __init__(self):
        pass

# just for testing
if __name__ == '__main__':
    a = TokBinOp('+')
    print a.getTokenName()


