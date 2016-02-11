import re
from SMMLexer import Lexer
from SMM_Memory import Stack, Store
class SMMInterpretor:
    """The interpreter class for SMM"""
    def __init__(self, instlist=[], symtab={}):
        self.__smm_instlist = instlist
        self.__smm_symtab = symtab
        self.__PC = 0
        self.__stack = Stack()
        self.__store = Store()

    def run(self):
        if __debug__:
            print '[SMM]Inst List: '+str(self.__smm_instlist.getInstsName())
            print '[SMM]Symbol Table: '+str(self.__smm_symtab.getTable())
        while self.__PC <= self.__smm_instlist.getInsts()[-1].getAddr():
            currInst = self.__smm_instlist.fetchInst(self.__PC)
            opcode = currInst.getOPCode()
            if __debug__:
                print "[SMM]PC: "+str(self.__PC)
                print "[SMM]Current Inst: "+opcode
                print "[SMM]Stack: "+str(self.__stack.getStack())
                print "[SMM]Store: "+str(self.__store.getStore())
            if re.match(r'^j\w+', opcode):#branch instructions
                label = currInst.getOperands()[0]
                shouldJmp = True
                if opcode == 'jmp':
                    shouldJmp = True
                else:
                    topval = self.__stack.pop()
                    if opcode == 'jz':
                        shouldJmp = int(topval) == 0
                    if opcode == 'jnz':
                        shouldJmp = int(topval) != 0
                if shouldJmp:
                    self.__PC = self.__smm_symtab.getVal(label)
                    continue
            if re.match(r'\bstore\b|\bload\b', opcode):#Store access instructions
                if opcode == 'load':
                    addr = self.__stack.pop()
                    val  = self.__store.load(addr)
                    self.__stack.push(val)
                else:
                    val = self.__stack.pop()
                    addr = self.__stack.pop()
                    self.__store.store(addr, val)
            if re.match(r'\bildc\b|\bpop\b|\bdup\b|\bswap\b', opcode):#Stack access instructions
                if opcode == 'ildc':
                    val = currInst.getOperands()[0]
                    self.__stack.push(val)
                if opcode == 'pop':
                    self.__stack.pop()
                if opcode == 'dup':
                    val = self.__stack.pop()
                    self.__stack.push(val)
                    self.__stack.push(val)
                if opcode == 'swap':
                    val1 = self.__stack.pop()
                    val2 = self.__stack.pop()
                    self.__stack.push(val1)
                    self.__stack.push(val2)
            if re.match(r'^i\w+', opcode) and (not re.match(r'ildc', opcode)):#binary ops--ps:why not name ildc "PUSH"!
                s_top1_val = int(self.__stack.pop())
                s_top2_val = int(self.__stack.pop())
                res = 0
                if opcode == 'iadd':
                    res = s_top1_val + s_top2_val
                if opcode == 'isub':
                    res = s_top2_val - s_top1_val
                if opcode == 'imul':
                    res = s_top1_val * s_top2_val
                if opcode == 'idiv':
                    res = s_top2_val / s_top1_val
                if opcode == 'imod':
                    res = s_top2_val % s_top1_val
                self.__stack.push(str(res))
            self.__PC += 1
        result = self.__stack.pop() # in compiled SC code, stack is empty in the end
        print result

    @staticmethod
    def bootstrap_smm(inpuBuf=''):
        smm_lexer = Lexer(inpuBuf)
        inst_list, symtab = smm_lexer.construct()
        smm_lexer.syntaxChecker(inst_list, symtab)
        interpreter = SMMInterpretor(inst_list, symtab)
        interpreter.run()


if __name__ == '__main__':
    SMMInterpretor.bootstrap_smm()

