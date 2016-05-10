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
        return "        {0} {1}{2:>14}".format(self.opcode, ', '.join(self.operandList), '')
        # return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)

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
        return "{0}:{1}".format(self.label_name, '#'+self.comment)


class IR_Method():
    def __init__(self, method_name, basic_blocks,allocator):
        self.name = method_name
        self.basic_blocks = basic_blocks
        for x in self.basic_blocks:
            x.method = self
        #stack_layout = [frame_size, [(IR*,vreg*,off*,L/S*, for_which_phi_if_any, pos)]]
        self.stack_layout = [0,[]]
        self.reg_allocator = allocator
        self.harvest_layout()
        self.print_layout()

    def get_basic_blocks(self):
        return self.basic_blocks

    def print_layout(self):
        print "Method:"+self.name,"***********"
        print "size:"+str(self.stack_layout[0])
        print "{0:>20}{1:>50}{2:>20}{3:>20}{4:>30}{5:>40}".format('IR','vreg','off','L/S','phi','pos')
        for tup in self.stack_layout[1]:
            print "{0:>50}{1:>20}{2:>20}{3:>20}{4:>40}{5:>30}".format(tup[0],tup[1],tup[2],tup[3],tup[4],tup[5])


    #stack_layout = [frame_size, [(IR_if_any,vreg,off,L/S, for_which_phi_if_any, pos)]]
    #NOTE: assumption, only for load we use pos, other cases, pos is 999999999
    def harvest_layout(self):
        reg_map = self.reg_allocator
        for b in self.basic_blocks:
            for i in b.insts:
                if(len(i.get_def())>0):
                    if(reg_map.v2p(i.get_def()[0]) in reg_map.callee_save_regs):
                        self.set_spilling(None, i.get_def()[0], 'store',None, 999999999999)#callee save, pos doesn't matter
                    for phi_usr in [x for x in i.get_def_refs() if isinstance(x, PHI_Node)]:
                        if(not isinstance(i, PHI_Node)):
                            self.set_spilling(i, i.get_def()[0],'store',phi_usr, 999999999999999)#phi-def IRs
                        else:
                            self.set_spilling(i, i.t ,'store',phi_usr, 999999999999999)#phi-def IRs


                if(i.comment not in ['MethodInvocationExpr', 'NewObjectExpr']):#a4- defs and uses
                    if(isinstance(i, PHI_Node)):
                        continue
                    if(len(i.get_def())>0 and i.get_def()[0][0] == 'a' and int(i.get_def()[0][1:])>3):
                        self.set_spilling(i, i.get_def()[0], 'store',None, i.define[0])
                    for pos in i.use:
                        if i.operandList[pos][0]=='a' and int(i.operandList[pos][1:])>3:
                            self.set_spilling(i, i.operandList[pos],'load',None,pos)






    def set_spilling(self, containing_node, vreg, l_or_s, phi, pos):
        curr_size = self.stack_layout[0]
        layout= self.stack_layout[1]#[(IR_if_any*,vreg*,off*,L/S*, for_which_phi_if_any, pos)]

        fp_local_off = 4
        if phi is not None:
            been_defined = [x for x in self.stack_layout[1] if phi is x[-2] and x[-3]=='store']
            assert(len(been_defined)<2)#1 or 0
            if(len(been_defined)==1):
                self.stack_layout[1] = layout + [(containing_node,vreg, been_defined[0][-4],'store',phi, pos)]#same offset
            else:#
                layout = layout + [(phi, phi.t, fp_local_off+curr_size,'load',None, 99999999999)]
                self.stack_layout[1] = layout + [(containing_node,vreg, fp_local_off + curr_size,'store',phi, pos)]#new offset
                curr_size+=4
        else:#spilling or a4 access
            if vreg[0] == 'a':
                self.stack_layout[1] = layout + [(containing_node, vreg, -4*int(vreg[1])+8, l_or_s, phi, pos)]
            else:
                assert(l_or_s == 'store')
                for usr in containing_node.get_def_refs():
                    for cur_pos in containing_node.user_index_look_up[usr]:
                        layout = layout + [(usr, vreg, fp_local_off + curr_size, 'load', phi, cur_pos)]
                self.stack_layout[1] = layout + [(containing_node, vreg, fp_local_off + curr_size, 'store', phi, pos)]
                curr_size += 4
        self.stack_layout[0] = curr_size







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
        self.comment = 'phi-node'

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
    # print ".static_data "+str(absmc.static_area[0])
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


# instruction selection part starts here
def instrSelection(bb_list, AR, reg_allocator):
    ir_code = []
    for bb in bb_list:
        ir_code += [bb.label]
        ir_code += bb.insts

    a_reg_cnt = 0 # count a4,... reg used before call
    reserved_reg = ['$v1','$s6','$s7']

    machine_code = []
    # insert prologue, pre-process spill
    # mem_s_ir = {ir: AR_offset}
    # mem_l_ir = {ir: [[pos,AR_offset],]}
    (mc,mem_s_ir,mem_l_ir) = insert_prologue(AR)
    machine_code += mc

    for ir in ir_code:
        def_spilled = False
        if ir in mem_s_ir:
            # if def spilled
            def_spilled = True
            def_spilled_ARoffset = mem_s_ir[ir]
            ir = IR(ir.opcode,['$v1']+ir.operandList[1:],ir.comment)

        if isinstance(ir, PHI_Node):
            offset = mem_l_ir[ir][0][1]
            machine_code += [MIPSCode('lw',['$v1','$fp',str(-offset)]),MIPSCode('move',[ir.get_def()[0],'$v1'])]

        elif isinstance(ir, IR):
            if ir in mem_l_ir:
                # if one or more use spilled
                spilled_uses = mem_l_ir[ir]
                # op_ls = ir.operandList[pos]

                use_spilled_cnt = 0
                for pos,offset in spilled_uses:
                    r_reg = reserved_reg[use_spilled_cnt]

                    ir = IR(ir.opcode,ir.operandList,ir.comment)
                    ir.operandList[pos] = r_reg
                    # if pos == 0:
                    #     ir = IR(ir.opcode,[r_reg]+op_ls[1:],ir.comment)
                    # elif pos == 1:
                    #     if len(op_ls) == 2:
                    #         ir = IR(ir.opcode,op_ls[0]+[r_reg],ir.comment)
                    #     else:
                    #         assert len(op_ls) == 3
                    #         ir = IR(ir.opcode,op_ls[0]+[r_reg]+[op_ls[2]],ir.comment)
                    # else:
                    #     assert pos == 2
                    #     ir = IR(ir.opcode,op_ls[:-1]+[r_reg],ir.comment)

                    machine_code += [MIPSCode('lw',[r_reg,'$fp',str(-offset)])]

                    use_spilled_cnt += 1


            opcode = ir.opcode
            operand = ir.operandList

            cm = {'move':'move'} # cur_map
            if opcode in cm:
                ir_def = ir.get_def()[0]
                if ir.comment in ['MethodInvocationExpr','NewObjectExpr'] and \
                ir_def[0] == 'a' and int(ir_def[1:]) >= 4:
                    # e.g. move a4, $t1 before call instr
                    machine_code += [MIPSCode('addi',['$sp','$sp','-4']),MIPSCode('sw',[ir.operandList[1],'$sp','0'])]
                    a_reg_cnt += 1
                else:
                    # normal move
                    # optimization
                    o1 = reg_allocator.v2p(ir.operandList[0])
                    o2 = reg_allocator.v2p(ir.operandList[1])
                    if not (o1[0] != 'a' and o1 == o2):
                        machine_code += [MIPSCode(cm[opcode],operand)]

            cm = {'move_immed_i':'li','iadd':'add','isub':'sub'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand)]

            cm = {'imul':'mult'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[1:]), \
                                 MIPSCode('mflo',[operand[0]])] # TODO: handle hi for mult
            cm = {'idiv':'div','imod':'div'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand[1:])] # stores the quotient in $LO and the remainder in $HI
                if opcode == 'idiv':
                    machine_code += [MIPSCode('mflo',[operand[0]])]
                else:
                    machine_code += [MIPSCode('mfhi',[operand[0]])]

            cm = {'igt':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],operand[2],operand[1]])]
            cm = {'igeq':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand),MIPSCode('xori',[operand[0],operand[0],'1'])]
            cm = {'ilt':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],operand)]
            cm = {'ileq':'slt'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],operand[2],operand[1]]),MIPSCode('xori',[operand[0],operand[0],'1'])]

            cm = {'bz':'beq','bnz':'bne'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],'$zero',operand[1]])]
            cm = {'jmp':'j'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0]])]

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
                machine_code += [MIPSCode(cm[opcode],[operand[0]]),MIPSCode('addi',['$sp','$sp',str(4*a_reg_cnt)])]
                a_reg_cnt = 0

            cm = {'ret':'jr'}
            if opcode in cm:
                # insert epilogue
                machine_code += insert_epilogue(AR)
                machine_code += [MIPSCode('move',['$v0','$a0']),MIPSCode(cm[opcode],['$ra'])]

            cm = {'save':'sw'}
            if opcode in cm:
                machine_code += [MIPSCode('addi',['$sp','$sp','-4']),MIPSCode(cm[opcode],[operand[0],'$sp','0'])]

            cm = {'restore':'lw'}
            if opcode in cm:
                machine_code += [MIPSCode(cm[opcode],[operand[0],'$sp','0']),MIPSCode('addi',['$sp','$sp','4'])]

        else: # label
            assert isinstance(ir,str)
            machine_code.append(ir+':')


        # add sw instr if def_spilled
        if def_spilled:
            machine_code += [MIPSCode('sw',['$v1','$fp',def_spilled_ARoffset])]

    # v2p
    for mc in machine_code:
        if isinstance(mc,MIPSCode):
            mc.MIPSv2p(reg_allocator)

    return machine_code

def insert_prologue(AR):
    #AR = [frame_size, mapping{stack_saved_reg: [offset, IR_or_PhiNode]}]
    mem_s_ir = {} # {ir: AR_offset}
    mem_l_ir = {} # {ir: [[pos,AR_offset],]}

    # push $ra, push $fp, allocate stack frame
    machine_code = [MIPSCode('sw',['$ra','$sp','-4']),MIPSCode('sw',['$fp','$sp','-8']),\
                    MIPSCode('addi',['$sp','$sp','-8']),MIPSCode('move',['$fp','$sp']),\
                    MIPSCode('addi',['$sp','$sp',str(-AR[0])])]

    # push callee-saved & spilled registers
    stack_layout = AR[1] # list of tuples
    for ir_ref,vreg,offset,action,phi_ref,pos in stack_layout:
        if ir_ref is None:
            # callee-saved registers
            machine_code += [MIPSCode('sw',[vreg,'$fp',offset])]
        else:
            # spilled registers or phi nodes
            if action == 'store':
                mem_s_ir[ir_ref] = offset
            else:
                assert action == 'load'
                if ir_ref not in mem_l_ir:
                    mem_l_ir[ir_ref] = [[pos,offset]]
                else:
                    mem_l_ir[ir_ref].append([pos,offset])

    return machine_code,mem_s_ir,mem_l_ir

def insert_epilogue(AR):
    machine_code = []
    # pop callee-saved registers
    stack_layout = AR[1] # list of tuples
    for ir_ref,vreg,offset,action,phi_ref,pos in stack_layout:
        if ir_ref is None:
            # callee-saved registers
            machine_code += [MIPSCode('lw',[vreg,'$fp',offset])]
    # destroy stack frame, pop $fp, pop $ra
    machine_code += [MIPSCode('addi',['$sp','$sp',str(AR[0]+8)]),\
                     MIPSCode('lw',['$ra','$sp','-4']),MIPSCode('lw',['$fp','$sp','-8'])]
    return machine_code

class MIPSCode:
    def __init__(self, opcode, operandList, comment=''):
        self.opcode = opcode
        # debug
        if not isinstance(operandList,list):
            print "operandList %s is not a list!" % operandList
        self.operandList = operandList

        self.comment = comment
        if comment is not '':
            self.comment = '# '+comment

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.opcode in ['lw','sw']: # self.operandList==[val,base,off]
            return "        {0} {1}, {3}({2}) {4}".format(self.opcode,self.operandList[0],\
                                                             self.operandList[1],self.operandList[2],self.comment)
                                                             # self.operandList[1],self.operandList[2], '#'+self.comment)
        else:
            self.operandList = [str(x) for x in self.operandList]
            return "        {0} {1} {2}".format(self.opcode, ', '.join(self.operandList),self.comment)
            # return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)

    def MIPSv2p(self,reg_allocator):
        operandList = self.operandList
        self.operandList = []
        for o in operandList:
            o = reg_allocator.v2p(o)
            if str(o)[0] in ['v','a','t','s']:
                o = '$'+o
            self.operandList.append(o)


