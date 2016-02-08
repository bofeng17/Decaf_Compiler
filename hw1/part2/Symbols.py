class SymTab:
    """Symbol table class for SC"""
    def __init__(self):
        self.__symbols = {}

    def hasSymbol(self, sym):
        return self.__symbols.has_key(sym)

    def addSymbol(self, sym, val):#inst_loc should be an idx of Instruction list
        self.__symbols[sym] = val

    def delSymbol(self, symbol): #No-op for SMM
        pass
    def getVal(self, symbol):
        return self.__symbols[symbol]
    def getTable(self):
        return self.__symbols
