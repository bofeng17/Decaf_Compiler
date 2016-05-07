import ast
import absmc

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


class Label():
    def __init__(self, label_name, comment="", indent=4):
        self.label_name = label_name
        self.comment = comment
        self.indent = indent
    def __str__(self):
        return "{0}:{1:>40}".format(self.label_name, '#'+self.comment)

#for BBLs, construct brand new insts as copy of the old insts, leave the old inst/label list alone
#and do the label patching on the new insts
class BasicBlock():
    def __init__(self, label):
        self.label = label
        self.insts = []
        self.preds = []
        self.succs = []

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

    #TODO: maintain same interface for phi_node and ir
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
    if ir.opcode in ['hload','halloc']:
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
