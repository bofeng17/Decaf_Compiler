#from codegen import IR
from analyses import Liveness

def instrSelection(ir_code):
    machine_code = []
    for ir in ir_code:
        if isinstance(ir, codegen.IR):
            opcode = ir.opcode
            operand = ir.operandList
            
            cm = {'move_immed_i':'li','move':'move','iadd':'add','isub':'sub'} # cur_map
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand)]
            
            cm = {'imul':'mult'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[1:]), \
                                 MIPSCode('mfhi',operand[0])] # TODO: hi for mult
            cm = {'idiv':'div','imod':'div'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[1:])] # stores the quotient in $LO and the remainder in $HI
                if opcode == 'idiv':
                    machine_code += [MIPSCode('mflo',operand[0])]
                else:
                    machine_code += [MIPSCode('mfhi',operand[0])]
            
            cm = {'igt':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],operand[2],operand[1]])]
            cm = {'igeq':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand),MIPSCode('xori',operand[0],operand[0],'1')]
            cm = {'ilt':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand)]
            cm = {'ileq':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],operand[2],operand[1]]),MIPSCode('xori',operand[0],operand[0],1)]
            
            cm = {'bz':'beq','bnz':'bne'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[0],'$zero',operand[1])]
            cm = {'jmp':'j'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[0])]

            cm = {'halloc':'syscall'}
            if opcode in cm: # TODO: check correctness of saving $a0
                machine_code += [MIPSCode('addi',['$sp','$sp','-4']),MIPSCode('sw',['$a0','$sp','0']),\
                                 MIPSCode('li',['$v0','9']),MIPSCode('move',['$a0',operand[1]]),\
                                 MIPSCode(cm[opcode]),MIPSCode('move',[operand[0],'$v0']),\
                                 MIPSCode('lw',['$a0','$sp','0']),MIPSCode('addi',['$sp','$sp','4'])]
            cm = {'hload':'lw'}
            if opcode in cm:
                machine_code += [MIPSCode('add','$v0',operand[1],operand[2]),MIPSCode(cm[opcode],operand[0],'$v0','0')]
            cm = {'hstore':'sw'}
            if opcode in cm:
                machine_code += [MIPSCode('add','$v0',operand[0],operand[1]),MIPSCode(cm[opcode],operand[2],'$v0','0')]

            cm = {'call':'jal'}
            if opcode in cm:
                # TODO: assert get_IN == get_OUT
#                live_vreg = list(Liveness(ir.basic_block.method).get_IN())
#                live_preg = []
#                for reg in live_vreg:
#                    live_preg.append(map_todo[reg]) # TODO: v-p map
#                for reg in live_preg:
#                    machine_code += [MIPSCode('addi',['$sp','$sp','-4']),MIPSCode('sw',[reg,'$sp','0'])]

                machine_code += [MIPSCode(cm[opcode],operand[0])]
                
#                for reg in live_preg[::-1]:
#                    machine_code += [MIPSCode('addi',['$sp','$sp','4']),MIPSCode('lw',[reg,'$sp','0'])]

            cm = {'ret':'jr'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],'$ra')]

            cm = {'save':'sw','restore':'lw'}
            if opcode in cm:
                pass

        else: # TODO: label
            machine_code.append(ir)

    return machine_code


class MIPSCode:
    def __init__(self, opcde, operandList, comment=''):
        self.opcde = opcde
        self.operandList = []
        for operand in operandList:
            if operandList[0] in ['v','a','t','s']:
                operand = '$'+operand
            self.operandList.append(operand)
        self.comment = comment

    def __str__(self):
        if self.opcode in ['lw','sw']: # self.operandList==[val,base,off]
            return "        {0} {1}, {3}({2}){4:>40}".format(self.opcode,self.operandList[0],\
                                                           self.operandList[1],self.operandList[2], '#'+self.comment)
        else:
            self.operandList = [str(x) for x in self.operandList]
            return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)
