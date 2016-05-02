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
    def __str__(self):
        self.operandList = [str(x) for x in self.operandList]
        return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)

    def set_start(self):
        self.start_inst = True
    def set_terminate(self):
        self.terminate_inst = True
    #labels is []
    def update_prepending_labels(self,labels):
        self.pre_labels = labels


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
    def update_pred(self, pred):
        self.preds += [pred]
    def update_succ(self, succ):
        self.succs += [succ]

    def print_bb(self, only_bb=False):
        print self.label+": "
        if only_bb:
            print "preds:",
            for each in self.preds:
                print '['+each.label+']',
            print "succs:",
            for each in self.succs:
                print '['+each.label+']',
            print ""
        else:
            for each in self.insts:
                print each



def emit_code(name):
    absmc.g_scan_static()
    absmc.g_obtain_cls_layouts()
    import sys
    sys.stdout = open(name+".ami", "w")
    print ".static_data "+str(absmc.static_area[0])
    for cid in ast.classtable:
        c = ast.classtable[cid]
        if(not c.builtin):
            c.genCode()
            c.printCode()
