class AST:
    """virtual class for all ASTs, main reason to have this parent class is
    in case any future usage that needs to add a common attribute to all derived ASTs"""
    def __init__(self, name):
        self._name = name
    def getName(self):
        return self._name

class BinOpExprAST(AST):
    """AST for the binary operations in SC"""
    def __init__(self, op, lnode, rnode):
        self._name = 'BinOpExprAST'
        self.__op = op
        self.__lnode = lnode
        self.__rnode = rnode
    def getOperator(self):
        return self.__op
    def getLeftNode(self):
        return self.__lnode
    def getRightNode(self):
        return self.__rnode

class ConstantAST(AST):
    """AST for integer constants"""
    def __init__(self, val):
        self._name = 'ConstantAST'
        self.__val = val

    def getVal(self):
        return self.__val;


class IdentiferAST(AST):
    """AST for Identifiers"""
    def __init__(self, id_name):
        self._name = 'IdentiferAST'
        self.__id_name = id_name

    def getIDName(self):
        return self.__id_name



class AssignStmtAST(AST):
    """This is for the only stmt--assignment statement, defined in the SC Spec"""
    def __init__(self, id_node, assignee):
        self.__id_node = id_node
        self.__assignee = assignee
        self._name = 'AssignStmtAST'

    def getIDNode(self):
        return self.__id_node

    def getAssignee(self):
        return self.__assignee
    # def emitCode(self):
        # assignee.emitCode()#now we have the val on top of stack





