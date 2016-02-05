class Instruction:
    """Instruction Class For SMM"""
    def __init__(self):
        self.__opcode = ''
        self.__operands = []
        self.__inst_loc = 0

    def getOPCode(self):
        return self.__opcode;

    def getOperands(self):
        return self.__operands;

    def addOperand(self, operand):
        self.__operands.append(operand)
    def setOPCode(self, opcode):
        self.__opcode = opcode
    def setInstLoc(self, inst_loc):
        self.__inst_loc = inst_loc
    def getAddr(self):
        return self.__inst_loc;


class InstList:
    """A list that contains a sequence of SMM assemblies"""
    def __init__(self):
        self.__inst_list = []

    def addInst(self, inst):
        self.__inst_list.append(inst)
    def getInsts(self):
        return self.__inst_list
    def getInstsName(self):
        nameList = []
        for inst in self.__inst_list:
            nameList.append((inst.getOPCode(), inst.getAddr()))
        return nameList
    def fetchInst(self, pc):
        return self.__inst_list[pc]

