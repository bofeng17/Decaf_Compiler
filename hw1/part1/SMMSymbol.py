"""Symbols in SMM(just label here)"""
class SymTab:
    """Symbol table class for SMM"""
    def __init__(self):
        self.__labels = {}

    def hasLabel(self, label):
        return self.__labels.has_key(label)

    def addLabel(self, label, inst_loc):#inst_loc should be an idx of Instruction list
        self.__labels[label] = inst_loc

    def delLabel(self, label): #No-op for SMM
        pass
    def getVal(self, label):
        return self.__labels[label]
    def getTable(self):
        return self.__labels
