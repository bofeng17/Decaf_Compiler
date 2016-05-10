import ast
import codegen
import analyses

#static area
#[area_size, {ID: offset}]
static_area = [0,{}]

def g_scan_static():
    global static_area
    for cid in ast.classtable:
        cur_cls = ast.classtable[cid]
        for fieldname in cur_cls.fields:
            cur_field = cur_cls.fields[fieldname]
            if cur_field.storage == 'static':
                static_area[1].update({cur_field.id:static_area[0]})
                static_area[0] += 1






#class layouts
#{class_name, layout}
class_layouts = {}
#layout
#[size, {field_ID:offset}]


def g_obtain_cls_layouts():
    global class_layouts
    for cid in ast.classtable:
        cur_cls = ast.classtable[cid]
        cls_tree = get_cls_tree(cur_cls)
        layout = build_layout(cls_tree)
        class_layouts.update({cur_cls.name: layout})




def build_layout(cls_tree):
    ret = [0,{}]
    for cur_cls in cls_tree:
        f_list = cur_cls.fields
        for f_id in f_list:
            f = f_list[f_id]
            if(f.storage != "static"):
                ret[1].update({f.id:ret[0]})
                ret[0] += 1
    return ret



def get_cls_tree(input_class):
    ret = [input_class]
    while(input_class.superclass != None):
        ret.insert(0,input_class.superclass)
        input_class = input_class.superclass
    return ret


def __get_next_inst(code,pos):
    ret = None
    for each in code[pos+1:]:
        if isinstance(each, codegen.IR):
            ret = each
            break
    return ret

def __get_pre_inst(code, pos):
    ret = None
    for each in code[pos-1::-1]:
        if isinstance(each, codegen.IR):
            ret = each
            break
    return ret

def __get_pre_labels(code, pos):
    ret = []
    for each in code[pos-1::-1]:
        if(isinstance(each, codegen.Label)):
            ret += [each.label_name]
        else:
            break
    return ret

#given code list, find first/last inst
def get_end_inst(insts, first=True):
    ret = None
    if first:
        ret = __get_next_inst(insts, 0)
    else:
        ret = __get_pre_inst(insts, len(insts))
    assert(ret!=None)
    return ret

#return the label, given str
def find_label(code, str_label):
    ret = None
    for each in code:
        if(isinstance(each, codegen.Label)):
            if(each.label_name == str_label):
                ret = each
                break
    assert(ret!=None)
    return ret


#given code list, and find the ir before the given ir_or_label
def get_pre_inst(code, ir_or_label):
    ret = None
    if isinstance(ir_or_label, codegen.IR):
        pos = code.index(ir_or_label)
    elif isinstance(ir_or_label, codegen.Label):
        pos = code.index(ir_or_label)
    else:
        pos = code.index(find_label(code, ir_or_label))
    ret = __get_pre_inst(code, pos)
    return ret
#given code list, and find the ir after the given ir_or_label
def get_next_inst(code, ir_or_label):
    ret = None
    if isinstance(ir_or_label, codegen.IR):
        pos = code.index(ir_or_label)
    elif isinstance(ir_or_label, codegen.Label):
        pos = code.index(ir_or_label)
    else:
        pos = code.index(find_label(code, ir_or_label))
    ret = __get_next_inst(code, pos)
    return ret

#given code list, and a ir, find all labels prepending this ir
def get_pred_labels(code, ir):
    assert(ir.start_inst)
    ret = __get_pre_labels(code, code.index(ir))
    return ret




#code will be discarded afterward
def build_basic_blocks(code):
    terminate_insts = ['bz','bnz','jmp','ret']
    ret_basic_blocks = []
    first_ir = get_end_inst(code)
    last_ir = get_end_inst(code, False)
    first_ir.set_start()
    last_ir.set_terminate()

    first_ir.update_prepending_labels(get_pred_labels(code,first_ir))
    #1st round--set up the markers
    for each in code:
        if isinstance(each, codegen.IR):
            if(each.opcode in terminate_insts):
                each.set_terminate()
                ir = get_next_inst(code,each)
                if(ir!=None):
                    ir.set_start()
                    ir.update_prepending_labels(get_pred_labels(code,ir))
                if(each.opcode != 'ret'):
                    ir = get_next_inst(code, each.operandList[-1])
                    if(ir is None):
                        continue
                    ir.set_start()
                    ir.update_prepending_labels(get_pred_labels(code,ir))
                    prev_ir = get_pre_inst(code,ir)
                    if(prev_ir != None):
                        prev_ir.set_terminate()

    #2nd round--construct basic blocks one by one
    in_bb = False
    bb = None
    for each in code:
        if isinstance(each, codegen.IR):
            if(each.start_inst):
                assert(not in_bb)
                bb = codegen.BasicBlock(get_new_block_label())
                in_bb = True
            if(each.terminate_inst):
                assert(in_bb)
                ret_basic_blocks.append(bb)
                in_bb = False
            if((not each.start_inst) and (not each.terminate_inst)):
                assert(in_bb)
            bb.add_inst(each)

    # for e in ret_basic_blocks:
        # e.print_bb()
    #3rd round--patch the labels used in ir
    for each in code:
        if isinstance(each, codegen.IR):
            if(each.opcode in ['jmp','bnz','bz']):#ir that needs to be patched
                dest_bb = find_bb(ret_basic_blocks, each.operandList[-1])
                # assert(dest_bb != None)
                if(dest_bb is None):
                    continue
                #patch the dest label===>>>>>>the ir in the bbls should change as well
                each.operandList[-1] = dest_bb.label

    # for e in ret_basic_blocks:
        # e.print_bb()
    #4th round--connect the bbls
    for bb in ret_basic_blocks:
        term_ir = bb.insts[-1]
        do_dest = False
        do_next = False
        if(term_ir.opcode in ['bz','bnz']):#dest and next
            do_dest = True
            do_next = True
        elif(term_ir.opcode in['jmp']):#dest only
            do_dest = True
            do_next = False
        elif(term_ir.opcode in ['ret']):#no next no dest
            do_dest = False
            do_next = False
        else:#next only
            do_dest = False
            do_next = True

        if(do_next):
            next_bb = find_next_bb(ret_basic_blocks, bb)
            if(next_bb != None):
                bb.update_succ(next_bb)
                next_bb.update_pred(bb)
        if(do_dest):
            dest_bb = find_bb(ret_basic_blocks, term_ir.operandList[-1])
            if(dest_bb is None):
                continue
            bb.update_succ(dest_bb)
            dest_bb.update_pred(bb)

    #5th round, eliminate unreachable bbls
    dead_bbls=[]
    for bb in ret_basic_blocks:
        if ret_basic_blocks.index(bb) == 0:#first bb is deem to not have preds
            continue
        if (len(bb.preds) == 0):
            dead_bbls.append(ret_basic_blocks.index(bb))
            for succ in bb.succs:
                succ.preds.remove(bb)
            ret_basic_blocks.remove(bb)

    return ret_basic_blocks

def find_next_bb(bbls, bb):
    if(bb is bbls[-1]):
        return None
    else:
        return bbls[bbls.index(bb)+1]


def find_bb(bbls, label):
    ret = None
    for bb in bbls:
        if((label in bb.insts[0].pre_labels) or (label == bb.label)):
            ret = bb
            break
    return ret




block_label_cnt = -1
def get_new_block_label():
    global block_label_cnt
    block_label_cnt += 1
    return 'BBL_'+str(block_label_cnt)


def remove_unneeded_saves(basic_blocks):
    liveness = analyses.Liveness(basic_blocks)
    for bb in basic_blocks:
        to_remove = []
        for i in bb.insts:
            if isinstance(i, codegen.IR) and i.opcode == 'save':
                out = liveness.get_OUT(i)
                if len(i.get_uses()) > 0 and i.get_uses()[0] not in out:
                    if i.get_uses()[0][0] == 'a' and int(i.get_uses()[0][1])<4:
                        continue
                    print "extra save:", i, out
                    to_remove += [i]
                    to_remove += [rt for rt in bb.insts if isinstance(rt,codegen.IR) and rt.opcode == 'restore' and rt.operandList[0] == i.get_uses()[0]]
        for i in to_remove:
            bb.remove_inst(i)




def convert_to_ssa(basic_blocks):
    remove_unneeded_saves(basic_blocks)
    no_more_phi = True
    first = True
    while(not no_more_phi or first):
        first = False
        no_more_phi = True
        reach_ana = analyses.ReachingDef(basic_blocks)
        for bb in basic_blocks:
            IN_SET = reach_ana.get_IN(bb)
            for ir in bb.insts:
                if(isinstance(ir, codegen.PHI_Node)):
                    continue
                uses = ir.get_uses()
                for u in uses:
                    #TODO:wtf
                    if u == 'sap' or u[0] == 'a':
                        continue
                    my_def = []
                    for x in bb.insts[bb.insts.index(ir)-1::-1]:
                        if u in x.get_def():
                            my_def = [x]
                            break
                    if(len(my_def)==0):
                        my_def = [x for x in IN_SET if u in x.get_def()]
                    # print "###########",ir.basic_block.label,ir.opcode,"use:",u
                    # for i in my_def:
                        # print "***",i.basic_block.label, i
                    if len(my_def) == 1:
                        ir.set_use_ref(my_def[0], uses.index(u))
                    elif len(my_def) >= 2:
                        global anti_loop
                        anti_loop = {}
                        phi_block,lir,rir = locate_in_1_1_block(bb,u,reach_ana)
                        if(phi_block is None):
                            print "We are done"
                            for la in basic_blocks:
                                la.print_bb()
                            assert(False)
                        # print "[caution!!!!]adding phi node for use:",u,"at block:",phi_block.label
                        phi = codegen.PHI_Node([lir,rir],phi_block)
                        phi.start_inst = True
                        phi_block.insts[0].start_inst = False
                        phi_block.insert_phi_inst(phi)
                        no_more_phi = False
                        break#break to ir
                    else:
                        assert(False)#should always have a def for each use
                if no_more_phi == False:#break to bb
                    break
            if no_more_phi == False:#break to while
                break

    test=[]
    for bb in basic_blocks:
        for i_or_p in bb.insts:
            #get new name for the def, and update all my users' use
            if(len(i_or_p.get_def())==0 or i_or_p.get_def()[0][0] == 'a'):
                continue
            new_name = codegen.number_it(i_or_p.get_def()[0])
            i_or_p.set_def(new_name)
            my_users = i_or_p.get_def_refs()
            for ur in my_users:
                # if(isinstance(ur,codegen.PHI_Node)):
                    # print bb.label, i_or_p,":", ur.basic_block.label, ur
                use_indexes = i_or_p.user_index_look_up[ur]
                map(lambda x: ur.set_use(new_name,x), use_indexes)

            if(isinstance(i_or_p,codegen.PHI_Node)):
                test += [i_or_p.l_ir, i_or_p.r_ir]



#Code testing if start and terminate insts set right
    # for b in basic_blocks:
        # print "-------",b.label,"---------"
        # for i in b.insts:
            # print i,":",i.start_inst,"is_terminate:",i.terminate_inst

    #set the preds and succs at each ir, for later liveness analysis usage
    for bb in basic_blocks:
        preds = bb.preds
        succs = bb.succs
        for ir in bb.insts:
            if ir.start_inst:
                ir.preds += [b.get_terminate_inst() for b in preds]
            if ir.terminate_inst:
                ir.succs += [b.get_start_inst() for b in succs]

#Code testing if pred and succs insts set right
    # for b in basic_blocks:
        # print "-------",b.label,"---------"
        # for i in b.insts:
            # print "IR:",i
            # print "preds:",
            # for u in i.preds:print u
            # print "succs:",
            # for u in i.succs:print u
    # print "NEW METHOD=======================--------------------------------------------===="
    # liveness = analyses.Liveness(basic_blocks)
    # for b in basic_blocks:
        # for ii in b.insts:
            # print '----------------------------------------------------------------'
            # print ii.basic_block.label, ii
            # print 'OUT=====***************************======='
            # for i in liveness.get_OUT(ii):print i,
            # print ""
            # print 'DEF======================================='
            # for i in ii.get_def():print i,
            # print ""
            # print 'USE========++++++++++++++++=============='
            # for i in ii.get_uses():print i,
            # print ""
            # print 'IN============--------------------======='
            # for i in liveness.get_IN(ii):print i,
            # print ""
    # tree = analyses.DominatorTree(basic_blocks)

    return basic_blocks


def traverse_domtree(tree_node,liveness):
    # if tree_node.basic_block.label == 'BBL_0' or tree_node.basic_block.label == 'BBL_16':
        # print tree_node.idomtees.pop(),"fuck"
    # worklist = [tree_node]
    # while(len(worklist)>0):
        # cur = worklist.pop(0)
        # for i in cur.idomtees:print i,cur
        # # print "LIVE:{",liveness.get_OUT(cur),"}"
        # if(len(cur.idomtees) > 0):
            # worklist += [x for x in cur.idomtees]
    print "ha:",tree_node, tree_node.basic_block.label
    for i in tree_node.idomtees:
        traverse_domtree(i,liveness)




#find the block which has two preds, and each pred's OUT for reachingdef has more than 1 but totall should be 2
#avaialble definition for the given var
anti_loop={}
def locate_in_1_1_block(bb, var, reachingdef):
    global anti_loop
    if(anti_loop.has_key(bb)):
        return None
    else:
        anti_loop[bb] = 1
    if len(bb.preds) == 0:
        return None
    while(len(bb.preds) == 1):
        # print "loop",bb.label,
        bb = bb.preds[0]
    # print bb.label, bb.preds
    pb1 = bb.preds[0]
    pb2 = bb.preds[1]
    OUT1 = reachingdef.get_OUT(pb1)
    OUT2 = reachingdef.get_OUT(pb2)
    defs1 = get_defs_from_OUT(OUT1, var)
    defs2 = get_defs_from_OUT(OUT2, var)

    # print"------------yoyoyoy=------------",bb.label, var
    # print"pb1:",pb1.label
    # for i in defs1:
        # print i.basic_block.label,i
    # print "=="
    # print"pb2:",pb2.label
    # for i in defs2:
        # print i.basic_block.label,i
    # print"------------yoyoyoy=------------"

    if(len(defs1) == 1 or len(defs2) == 1):
        if(len(set(defs1)|set(defs2)) == 2):
            if(defs1[0] is not defs2[0]):
                return (bb,defs1[0],defs2[0])
            else:
                if(len(defs1)>1):
                    return (bb,defs1[1],defs2[0])
                else:
                    return (bb,defs1[0],defs2[1])

    if(len(defs1)>1):
        ret=locate_in_1_1_block(pb1,var,reachingdef)
        if(ret!=None):
            return ret
    if(len(defs2)>1):
        ret=locate_in_1_1_block(pb2,var,reachingdef)
        if(ret!=None):
            return ret
    return (None,None,None)

def get_defs_from_OUT(OUT, var):
    return [x for x in OUT if var in x.get_def()]


#traverse the tree, and allocate reg for all defs,
#when doing so, all the uses of the def will also be updated
class Reg_allocator():
    def __init__(self, basic_blocks):
        self.basic_blocks = basic_blocks
        dom_tree = analyses.DominatorTree(self.basic_blocks)
        liveness = analyses.Liveness(self.basic_blocks)
        # traverse_domtree(dom_tree.root, liveness)
        self.dom_tree = dom_tree
        self.liveness = liveness
        self.ret_reg = ['v0']
        self.caller_save_regs = ['t'+str(x) for x in range(0,10)]
        self.callee_save_regs = ['s'+str(x) for x in range(0,6)]#take out two for mem-ops
        self.sap = ['gp']
        self.reg_pool = self.caller_save_regs+self.callee_save_regs
        self.res_men_regs = ['v1','s6','s7']
#{vreg, preg}
        self.mapping = {}
        self.allocate(self.dom_tree.root)

    def v2p(self, vreg):
        # if vreg[0] == 't':#only map t_regs
        #TODO: this is not the source of the bug, might want to debug this first when things go south
        if self.mapping.has_key(vreg):
            return self.mapping[vreg]
        return vreg
    def allocate(self, node):
        out_set = self.liveness.get_OUT(node)
        # print node.basic_block.label, node, node.get_def(), out_set, node.basic_block.label
        # print self.mapping
        if node is None:
            return
        if len(node.get_def())>0 and node.get_def()[0][0]=='t':
            if(len(self.mapping)==0):
                used_regs=[]
            else:
                used_regs = [self.mapping[x] for x in out_set if x != node.get_def()[0] and self.mapping.has_key(x)]
            new_reg = self.get_unused(used_regs)
            if(new_reg is None):
                #spilling
                node.basic_block.method.set_spilling(node, node.get_def()[0], 'store', None)
            else:
                self.mapping[node.get_def()[0]] = new_reg
        for sub in node.idomtees:
            self.allocate(sub)


        # for k in self.mapping:
            # print k,self.mapping[k]

    def get_unused(self, used):
        for reg in self.reg_pool:
            if(reg not in used):
                return reg
        return None







