import re
from SMMInst import InstList, Instruction
from SMMSymbol import SymTab
# from SMMInst import Instruction, InstList
class Lexer:
    """This Lexer class is not a traditional Lexer,
        Insted, it will parse the input buf, construct
        the symbol table and Instruction list"""
    def __init__(self, buf=''):
        # """Keywords for SMMINSTM"""
        self.__OPCODES = ('ildc', 'iadd', 'isub', 'imul', 'idiv',
                'imod', 'pop', 'dup', 'swap', 'jz' ,
                'jnz', 'jmp', 'load', 'store')

        # """Input program stream"""
        self.__ProgBuffer = buf

    def isLabel(self, s):
        if re.match(r'^\w[\w\d_]+$', s):
            return True
        return False
    def isIntNum(self, s):
        if re.match(r'^\-?\d+$', str(s)):
            return True
        return False
    def isOPCode(self, s):
        try:
            if self.__OPCODES.count(s) > 0:
                return True
            return False
        except (NameError, ValueError):
            pass

    def syntaxChecker(self, instList, symTab):
        for inst in instList.getInsts():
            if __debug__:
                print "Examing  "+str(inst.getOPCode())
            operands = inst.getOperands()
            opcode = inst.getOPCode()
            if __debug__:
                print "op: "+opcode+" operand len:"+str(len(operands))
            if re.match(r'ildc', opcode):
                assert len(operands) == 1 and self.isIntNum(operands[0]), "invalid operand[%r] for %r" % (operands, opcode)
            if re.match(r'\biadd\b|\bisub\b|\bimul\b|\bidiv\b|\bimod\b|\bpop\b|\bdup\b|\bswap\b|\bload\b|\bstore\b',opcode):
                assert len(operands) == 0, "%r's operand is illegal"%opcode
            if re.match(r'\bjz\b|\bjnz\b|\bjmp\b', opcode):
                assert len(operands) == 1 and self.isLabel(operands[0]), "invalid operand[%r] for %r" % (operands, opcode)
                assert symTab.hasLabel(operands[0]), "Label %r for opcode %r does not exist"%(operands, opcode)

    # """Process the input SMM program"""
    def startProcessInpuProg(self):
        currPC = 0
        symTab = SymTab()
        instList = InstList()
        currWord = ''
        currInst = Instruction()
        charIdx = 0
        if __debug__:
            print "input buffer: "+self.__ProgBuffer
        while charIdx < len(self.__ProgBuffer)-1:
            char = self.__ProgBuffer[charIdx]
            next_char = self.__ProgBuffer[charIdx+1]
            currWord = currWord.strip()
            if re.match(r'\s' ,char) and re.match(r'\s', next_char):
                charIdx += 1
                continue
            if char == ':':
                assert self.isLabel(currWord) and (not self.isOPCode(currWord)), "%r is not a valid label name" % currWord
                if currInst.getOPCode() != "":
                    currInst.setInstLoc(currPC)
                    instList.addInst(currInst)
                    if __debug__:
                        print '[SMM]Lexer: adding instruction[%r] addr: %r'%(currInst.getOPCode(),currPC)
                    currPC += 1
                    currInst = Instruction()#get a new Instruction object
                if __debug__:
                    print '[SMM]Lexer: adding label[%r] addr: %r'%(currWord,currPC)
                symTab.addLabel(currWord, currPC)
                currWord = ''
                charIdx += 1
                continue
            if re.match(r'\s' ,char) and currWord != '':
                if self.isOPCode(currWord):#find new opcode, save the "current" instruction if exist
                    if currInst.getOPCode() != "":
                        currInst.setInstLoc(currPC)
                        instList.addInst(currInst)
                        if __debug__:
                            print '[SMM]Lexer: adding instruction[%r] addr: %r'%(currInst.getOPCode(),currPC)
                        currPC += 1
                        currInst = Instruction()#get a new Instruction object
                    if __debug__:
                        print '[SMM]Lexer: set opcode[%r] addr: %r'%(currWord,currPC)
                    currInst.setOPCode(currWord)
                    currWord = ''
                    charIdx += 1
                    continue
                #if not opcode, it should be an operand, then assert we already found opcode of currinst
                assert currInst.getOPCode() != "", "%r is not a valid opcode" % currWord
                if __debug__:
                    print '[SMM]Lexer: adding operand[%r] for: %r'%(currWord, currInst.getOPCode())
                currInst.addOperand(currWord)
                currWord = ''
                charIdx += 1
                continue
            currWord += char
            charIdx += 1
            continue
        if currInst.getOPCode != '':
            currInst.setInstLoc(currPC)
            instList.addInst(currInst)
        return (instList, symTab)



    def getInpuProg(self):
        print "Please input SMM program, press <Ctrl-D> when finish"
        while True:
            try:
                s = raw_input()
                hash_idx = s.find('#');
                if hash_idx > 0:
                    s = s[:hash_idx]
                if hash_idx == 0:
                    s = ''
                self.__ProgBuffer += s
                self.__ProgBuffer += ' '
            except EOFError:
                self.__ProgBuffer += '$'
                print 'Result: '
                break

    # """Parse the inpu buffer and construct the instruction list and symbol table"""
    def construct(self):
        self.getInpuProg()
        insts, symtab = self.startProcessInpuProg()
        return (insts, symtab)

