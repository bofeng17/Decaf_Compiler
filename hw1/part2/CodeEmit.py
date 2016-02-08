class CodeEmitter:
    """Code emitter for SC"""
    def __init__(self, symTab):
        self.__symTab = symTab
        self.__unusedAddr = 0
        self.__binOpTranslateTab = {'+': 'iadd', '-': 'isub', '*': 'imul', '/': 'idiv', '%': 'imod'}

    def checkIDExist(self, binAST):
        idname = binAST.getIDName()
        assert self.__symTab.hasSymbol(idname),"%r is not initializaed!"%idname

    def emitCode(self, AST):
        if AST.getName() == 'ConstantAST':
            print "ildc %r"%AST.getVal();

        elif AST.getName() == 'IdentiferAST':
        #create an entry in SymTab if ID not exist, otherwise just emit the symbol location
            id_name = AST.getIDName()
            if not self.__symTab.hasSymbol(id_name):
                newAddr = self.__unusedAddr
                self.__symTab.addSymbol(id_name, newAddr)
                self.__unusedAddr += 1

            print "ildc %r" %self.__symTab.getVal(id_name)

        elif AST.getName() == 'BinOpExprAST':
            op = AST.getOperator()
            lnode = AST.getLeftNode()
            rnode = AST.getRightNode()

            #lnode val in stack
            if lnode.getName() == 'IdentiferAST':
                self.checkIDExist(lnode)
                self.emitCode(lnode)
                print "load"
            else:
                self.emitCode(lnode)
            #rnode val in stack
            if rnode.getName() == 'IdentiferAST':
                self.checkIDExist(rnode)
                self.emitCode(rnode)
                print "load"
            else:
                self.emitCode(rnode)

            print self.__binOpTranslateTab[op]



        elif AST.getName() == 'AssignStmtAST':
            id_node = AST.getIDNode()
            assignee = AST.getAssignee()

            self.emitCode(id_node)#var addr in stack

            #val in stack
            if assignee.getName() == 'IdentiferAST':
                self.checkIDExist(assignee)
                self.emitCode(assignee)
                print "load"
            else:
                self.emitCode(assignee)

            print "store"

        else:
            assert False, "Cannot handle unknown AST[%r]"%AST.getName()

