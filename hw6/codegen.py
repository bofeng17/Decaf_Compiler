import ast
import absmc,analyses

class IR():
    def __init__(self, opcode, operandList, comment=""):
        self.opcode = opcode
        self.operandList = operandList
        self.comment = comment
        self.start_inst = False
        self.terminate_inst = False
        self.pre_labels = None
        #precompute the fields below
        self.preds = []
        self.succs = []
        self.define = []#the pos of the def
        self.use = []#the pos of the uses
        self.use_ref = []#for each use, referencing the def ir
        self.def_ref = []#for the def, referencing all the uses irs
        set_defuse(self)
#{user:[use_index]}, for an ir, the users of my def are IRs, but we need to know the exact indexs of the use in my user
        self.user_index_look_up = {}
        self.basic_block = None


#for dominator tree
        self.dominators = set()
        self.dominatees = set()
        self.idomtors = set()
        self.idomtees = set()

#for reg_mapping
        self.reg_mapping = None
    def set_idomtees(self, my_idomtees):
        # for idomtee in self.idomtees:
            # idomtee.idomtors.remove(self)
        # self.idomtees = set()
        for idomtee in my_idomtees:
            self.idomtees.add(idomtee)
            idomtee.idomtors.add(self)
    def set_dominators(self,my_domtors):
        for domtor in self.dominators:
            domtor.dominatees.remove(self)
        self.dominators = set()
        for domtor in my_domtors:
            self.dominators.add(domtor)
            domtor.dominatees.add(self)

    def __str__(self):
        if self.reg_mapping is not None:
            self.operandList = [self.reg_mapping.v2p(str(x)) for x in self.operandList]
        else:
            self.operandList = [str(x) for x in self.operandList]
        return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)

    def set_start(self):
        self.start_inst = True
    def set_terminate(self):
        self.terminate_inst = True
    #labels is []
    def update_prepending_labels(self,labels):
        self.pre_labels = labels

    def get_basic_block(self):
        return self.basic_block


###!!!!!!!!!!!!!!!!!only interact with defs and uses using the methods
    def get_def(self):
        return [self.operandList[x] for x in self.define]
    def get_uses(self):
        # if(len(self.use_ref)>0):
            # return [x.get_def()[0] for x in self.use_ref]
        # else:
            return [self.operandList[x] for x in self.use]

    def set_def(self, var):#update the name of the def
        self.operandList[self.define[0]] = var
    def set_use(self, var, pos):#NOTE: Convert pos for uses to pos in operandlist first!
        self.operandList[self.use_pos_to_operand_pos(pos)] = var

    def use_pos_to_operand_pos(self, use_pos):
        return self.use[use_pos]

#NOTE: this pos is for the use_ref,  not for operandlist!!!!!
    def set_use_ref(self, ir, pos):#for this ir's given use, bind it to its ref
        self.use_ref.insert(pos, ir)
        self.set_use(ir.get_def()[0],pos)#updating the name of the use to the ref's def name
        #for the given def ir, add myself to its def_ref
        ir.add_def_ref(self,pos)

    def add_def_ref(self,use_ir, use_index):#for this ir's given def, bind it to all its refs(the irs that use this def)
        self.def_ref.append(use_ir)
        if self.user_index_look_up.has_key(use_ir):
            self.user_index_look_up[use_ir].append(use_index)
        else:
            self.user_index_look_up[use_ir] = []
            self.user_index_look_up[use_ir].append(use_index)


    def get_def_refs(self):#get the references to this ir's def
        return self.def_ref
    def get_use_ref(self, use):#get the reference to this ir's given use name
        return self.use_ref[self.get_uses.index(use)]

    def is_defined(self, var):
        return var in self.get_def()
    def is_used(self, var):
        return var in self.get_uses()
    def phi_use_ref(self):
        return []####only for compatible reason


class Label():#No-longer use after basic block construction
    def __init__(self, label_name, comment="", indent=4):
        self.label_name = label_name
        self.comment = comment
        self.indent = indent
    def __str__(self):
        return "{0}:{1:>40}".format(self.label_name, '#'+self.comment)


class Method():
    def __init__(self, method_name, basic_blocks):
        self.name = method_name
        self.basic_blocks = basic_blocks

        #stack_layout = [frame_size, mapping{stack_saved_reg ,offset}]
        self.stack_layout = [0,{}]


    def get_basic_blocks(self):
        return self.basic_blocks




#for BBLs, construct brand new insts as copy of the old insts, leave the old inst/label list alone
#and do the label patching on the new insts
class BasicBlock():
    def __init__(self, label):
        self.label = label
        self.insts = []
        self.preds = []
        self.succs = []
        self.method = None

    def add_inst(self, inst):
        self.insts += [inst]
        inst.basic_block = self
        if(len(self.insts)>1):
            self.insts[-1].preds += [self.insts[-2]]
            self.insts[-2].succs += [self.insts[-1]]

    def insert_phi_inst(self, phi_inst):
        #only deal with the pred,succ inside this bbl
        self.insts.insert(0, phi_inst)
        if(len(self.insts)>1):
            self.insts[0].succs += [self.insts[1]]
            self.insts[1].preds += [self.insts[0]]

    def remove_inst(self, inst):
        for p in inst.preds:
            for s in inst.succs:
                p.succs.append(s)
                s.preds.append(p)
        for p in inst.preds:
            p.succs.remove(inst)
        for s in inst.succs:
            s.preds.remove(inst)
        self.insts.remove(inst)

    def insert_inst_before(self, inst, new_inst):
        pass

    def update_pred(self, pred):
        self.preds += [pred]
    def update_succ(self, succ):
        self.succs += [succ]

    def get_start_inst(self):
        return self.insts[0]
    def get_terminate_inst(self):
        return self.insts[-1]
    def print_bb(self, reg_allocator,only_code=False):
        print self.label+": "
        if not only_code:
            print "#preds:",
            for each in self.preds:
                print '['+each.label+']',
            print "succs:",
            for each in self.succs:
                print '['+each.label+']',
            print ""
        for each in self.insts:
            # print each.start_inst,each.terminate_inst, each
            # print 'preds[{0}]'.format(','.join(x.__str__() for x in each.preds))
            # print 'succs[{0}]'.format(','.join(x.__str__() for x in each.succs))
            # print
            # print
            each.reg_mapping = reg_allocator
            #Hack: remove "move, reg, reg" deadcode
            if(reg_allocator is not None and isinstance(each,IR) and each.opcode == 'move' and reg_allocator.v2p(each.get_uses()[0]) == reg_allocator.v2p(each.get_def()[0])):
                continue
            print each


class PHI_Node():
    def __init__(self, defs, basic_block):
        self.t = defs[0].get_def()[0]
        self.l_ir = defs[0]
        self.r_ir = defs[1]
        self.l_ir.add_def_ref(self,0)
        self.r_ir.add_def_ref(self,1)
        self.lblock = self.l_ir.get_basic_block()
        self.rblock = self.r_ir.get_basic_block()
        self.use_ref = [self.l_ir, self.r_ir]
        self.def_ref = []
        self.preds = []
        self.succs = []
        self.basic_block = basic_block

        self.start_inst = False
        self.terminate_inst = False

#{user:[use_index]}, for an ir, the users of my def are IRs, but we need to know the exact indexs of the use in my user
        self.user_index_look_up = {}
#for dominator tree
        self.dominators = set()
        self.dominatees = set()
        self.idomtors = set()
        self.idomtees = set()
#for reg_allocator
        self.reg_mapping = None

    def set_idomtees(self, my_idomtees):
        # for idomtee in self.idomtees:
            # idomtee.idomtors.remove(self)
        # self.idomtees = set()
        for idomtee in my_idomtees:
            if idomtee is self:
                continue
            self.idomtees.add(idomtee)
            idomtee.idomtors.add(self)

    def set_dominators(self,my_domtors):
        for domtor in self.dominators:
            domtor.dominatees.remove(self)
        self.dominators = set()
        for domtor in my_domtors:
            self.dominators.add(domtor)
            domtor.dominatees.add(self)

    def __str__(self):
        if self.reg_mapping is not None:
            reg_mapping = self.reg_mapping
            return "        {0} = phi [{1}, {2}]  [{3}, {4}]".format(reg_mapping.v2p(self.t),\
                                                     reg_mapping.v2p(self.get_uses()[0]), reg_mapping.v2p(self.get_uses()[1]),\
                                                     self.lblock.label,self.rblock.label)
        else:
            return "        {0} = phi [{1}, {2}]  [{3}, {4}]".format(self.t,\
                                                     self.get_uses()[0], self.get_uses()[1],\
                                                     self.lblock.label,self.rblock.label)

    def get_def(self):#return name
        return [self.t]
    def get_uses(self):#return names
        return [x.get_def()[0] for x in self.use_ref]#when numbering, the results will be automatically updated

    def get_def_refs(self):#return the references to this ir's def
        return self.def_ref
    def get_use_ref(self, name_of_use):#return the ir reference to this ir's given use name
        return self.use_ref[self.get_uses().index(name_of_use)]
    def get_basic_block(self):
        return self.basic_block

    #NOTE: maintain same interface for phi_node and ir
    def set_def(self, var):#update the name of the def
        self.t = var
    def set_use(self, var, pos):
        self.use_ref[pos].get_def()[0], var

    def set_use_ref(self, ir, pos):#for this ir's given use, bind it to its ref
        #for the given def ir, add myself to its def_ref
        ir.add_def_ref(self,pos)

    def add_def_ref(self,use_ir, use_index):#for this ir's given def, bind it to all its refs(the irs that use this def)
        self.def_ref.append(use_ir)
        if self.user_index_look_up.has_key(use_ir):
            self.user_index_look_up[use_ir].append(use_index)
        else:
            self.user_index_look_up[use_ir] = []
            self.user_index_look_up[use_ir].append(use_index)

    def phi_use_ref(self):
        return self.use_ref

def emit_code(name):
    absmc.g_scan_static()
    absmc.g_obtain_cls_layouts()
    # import sys
    # sys.stdout = open(name+".ami", "w")
    print ".static_data "+str(absmc.static_area[0])
    for cid in ast.classtable:
        c = ast.classtable[cid]
        if(not c.builtin):
            c.genCode()
            c.printCode()


#this only mark the pos of def/uses for each ir
def set_defuse(ir):
    if ir.opcode in ['iadd','isub','imul','idiv','imod','igt','igeq','ilt','ileq']:
        ir.define = list([0])
        ir.use = list([1,2])
    if ir.opcode in ['fadd','fsub','fmul','fdiv','fmod','fgt','fgeq','flt','fleq']:
        ir.define = list([0])
        ir.use = list([1,2])
    if ir.opcode in ['ftoi','itof']:
        ir.define = list([0])
        ir.use = list([1])
    if ir.opcode in ['bz','bnz']:
        ir.use = list([0])
    if ir.opcode in ['hload']:
        ir.define = list([0])
        ir.use = list([1,2])
    if ir.opcode in ['halloc']:
        ir.define = list([0])
        ir.use = list([1])
    if ir.opcode in ['hstore']:
        ir.use = list([0,1,2])
    if ir.opcode in ['save']:
        ir.use = list([0])
    if ir.opcode in ['restore']:
        ir.define = list([0])
    if ir.opcode in ['move']:
        ir.define = list([0])
        ir.use = list([1])
    if ir.opcode in ['move_immed_i','move_immed_f']:
        ir.define = list([0])

#{name:version number}
var_number = {}
def number_it(var_name):
    global var_number
    if var_number.has_key(var_name):
        var_number[var_name] += 1
    else:
        var_number[var_name] = -1#start with 0
        var_number[var_name] += 1

    return var_name + '_'+str(var_number[var_name])

def instrSelection(ir_code):
    machine_code = []
    for ir in ir_code:
        if isinstance(ir, IR):
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
                machine_code += [MIPSCode(cm[opcode],[operand[0],operand[2],operand[1]]),MIPSCode('xori',operand[0],operand[0],'1')]

            cm = {'bz':'beq','bnz':'bne'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],'$zero',operand[1]])]
            cm = {'jmp':'j'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[0])]

            cm = {'halloc':'syscall'}
            if opcode in cm: # TODO: check correctness of saving $a0
                machine_code += [MIPSCode('addi',['$sp','$sp','-4']),MIPSCode('sw',['$a0','$sp','0']),\
                                 MIPSCode('li',['$v0','9']),MIPSCode('move',['$a0',operand[1]]),\
                                 MIPSCode(cm[opcode],[]),MIPSCode('move',[operand[0],'$v0']),\
                                 MIPSCode('lw',['$a0','$sp','0']),MIPSCode('addi',['$sp','$sp','4'])]
            cm = {'hload':'lw'}
            if opcode in cm:
                machine_code += [MIPSCode('add',['$v0',operand[1],operand[2]]),MIPSCode(cm[opcode],[operand[0],'$v0','0'])]
            cm = {'hstore':'sw'}
            if opcode in cm:
                machine_code += [MIPSCode('add',['$v0',operand[0],operand[1]]),MIPSCode(cm[opcode],[operand[2],'$v0','0'])]

            cm = {'call':'jal'}
            if opcode in cm:
                # TODO: assert get_IN == get_OUT
#                live_vreg = list(analyses.Liveness(ir.basic_block.method).get_IN())
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
                machine_code += [MIPSCode('move',['$v0','$a0']),MIPSCode(cm[opcode],['$ra'])]

            cm = {'save':'sw','restore':'lw'}
            if opcode in cm:
                pass

        else: # TODO: label
            machine_code.append(ir)

    print machine_code
    return machine_code


class MIPSCode:
    def __init__(self, opcode, operandList, comment=''):
        self.opcode = opcode
        self.operandList = []
        for operand in operandList:
            if str(operand)[0] in ['v','a','t','s']:
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


