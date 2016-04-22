import ast
import absmc
class IR():
    def __init__(self, opcode, operandList, comment=""):
        self.opcode = opcode
        self.operandList = operandList
        self.comment = comment
    def __str__(self):
        self.operandList = [str(x) for x in self.operandList]
        return "        {0} {1}{2:>40}".format(self.opcode, ', '.join(self.operandList), '#'+self.comment)


class Label():
    def __init__(self, label_name, comment="", indent=4):
        self.label_name = label_name
        self.comment = comment
        self.indent = indent
    def __str__(self):
        return "{0}:{1:>40}".format(self.label_name, '#'+self.comment)

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
