import ast
import codegen

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

#scan through the bbls, for each br inst, patch the label of the target to the bbl label
#also setup pred and succ edges properly for the involed bbls
def update_label(basic_blocks):
    pass



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
                assert(dest_bb != None)
                #patch the dest label===>>>>>>the ir in the bbls should change as well
                #TODO: verify this
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
            bb.update_succ(dest_bb)
            dest_bb.update_pred(bb)

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
