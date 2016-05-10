import codegen
#IN and OUT and gen and kill have element type IR
#results: {BB,INs,OUTs}
#middle_value: [converged, {BB, [INs,OUTs]}]
class ReachingDef():
    def __init__(self, BBLs):
        bbls = list(BBLs)
        self.basic_blocks = bbls
        self.initialize()
        self.compute()
    def get_IN(self, bb):
        return self.results[bb][0]
    def get_OUT(self, bb):
        return self.results[bb][1]

    def initialize(self):
        converged = False
        self.middle_value = [converged, {}]
        for b in self.basic_blocks:
            #empty originally
            in_set = set()
            out_set = set()
            self.middle_value[1][b] = [in_set,out_set]
        self.iterate(first=True)
    def get_gen_set(self, b):
        return set([x for x in b.insts if  len(x.get_def())>0 and x.get_def()[0] not in [t.get_def()[0] for t in b.insts[b.insts.index(x)+1:] if len(t.get_def())>0]])
    def get_kill_set(self, b):
        cur_IN = self.middle_value[1][b][0]
        cur_gen = self.get_gen_set(b)
        #compatible with both IR and Phi_node
        return set([x for x in cur_IN if (x in x.phi_use_ref() or (x.get_def()[0] in [y.get_def()[0] for y in cur_gen]))])
        # return set([x for x in cur_IN if ( (x.get_def()[0] in [y.get_def()[0] for y in cur_gen]))])
    def iterate(self, first = False):
        converged = True
        for bb in self.basic_blocks:
            preds = bb.preds
            before = set(self.middle_value[1][bb][0])
            self.middle_value[1][bb][0] = set().union(*[self.middle_value[1][pred][1] for pred in preds])
            converged = converged and not has_change(self.middle_value[1][bb][0],before)
            before = set(self.middle_value[1][bb][1])
            self.middle_value[1][bb][1] = (self.middle_value[1][bb][0]-self.get_kill_set(bb)) | self.get_gen_set(bb)
            converged = converged and not has_change(self.middle_value[1][bb][1],before)
#Comment this out, dont'delete
            # if(bb.label=='BBL_5'):
                # print '\t\t\t\tIN============--------------------======='
                # for i in self.middle_value[1][bb][0]:
                    # print "\t\t\t\t",i.basic_block.label, i
                # print '\t\t\t\tKILL======================================='
                # for i in self.get_kill_set(bb):
                    # print "\t\t\t\t",i.basic_block.label, i
                # print '\t\t\t\tGEN========++++++++++++++++=============='
                # for i in self.get_gen_set(bb):
                    # print "\t\t\t\t",i.basic_block.label, i
                # print '\t\t\t\tOUT=====***************************======='
                # for i in self.middle_value[1][bb][1]:
                    # print "\t\t\t\t",i.basic_block.label, i
        if(not first):
            self.middle_value[0] = converged
        else:
            self.middle_value[0] = False

    def compute(self):
        first = True
        while(not self.middle_value[0]):
            self.iterate(first)
            first = False
        self.results = self.middle_value[1]


#IN and OUT and use and def have element type var name
#results: {S,INs,OUTs}
#middle_value: [converged, {S, [INs,OUTs]}]
class Liveness():
    def __init__(self, BBLs, ssa=True):
        self.basic_blocks = BBLs
        self.ssa =ssa
        self.initialize()
        self.compute()

    def get_IN(self, s):
        return self.results[s][0]
    def get_OUT(self, s):
        return self.results[s][1]

    def compute(self):
        first = True
        while(not self.middle_value[0]):
            self.iterate(first)
            first = False
        self.results = self.middle_value[1]

    def initialize(self):
        converged = False
        self.middle_value = [converged, {}]
        for b in self.basic_blocks:
            for i in b.insts:
                #empty originally
                in_set = set()
                out_set = set()
                self.middle_value[1][i] = [in_set,out_set]
        self.iterate(first=True)

    def get_def_set(self, i):
        if(not self.ssa and isinstance(i,codegen.IR) and i.opcode in['save','restore']):
            return set([])
        return set([x for x in i.get_def() if x[0]=='t'])
    def get_use_set(self,i):
        if(not self.ssa and isinstance(i,codegen.IR) and i.opcode in['save','restore']):
            return set([])
        if(isinstance(i,codegen.PHI_Node)):
            return set([])
        else:
            return set([x for x in i.get_uses() if x[0]=='t'])
    def iterate(self, first = False):
        converged = True
        for bb in self.basic_blocks:
            for i in bb.insts:
                succs = i.succs
                before = set(self.middle_value[1][i][1])
                self.middle_value[1][i][1] = set().union(*[self.middle_value[1][succ][0] for succ in succs])
                converged = converged and not has_change(self.middle_value[1][i][1],before)
                before = set(self.middle_value[1][i][0])
                self.middle_value[1][i][0] = (self.middle_value[1][i][1]-self.get_def_set(i)) | self.get_use_set(i)
                converged = converged and not has_change(self.middle_value[1][i][0],before)
            if(not first):
                self.middle_value[0] = converged
            else:
                self.middle_value[0] = False

            # if(bb.label=='BBL_5' and self.ssa ):
                # for i in bb.insts:
                    # print i
                    # print '\t\t\t\tOUT=====***************************======='
                    # for i2 in self.middle_value[1][i][1]:
                        # print "\t\t\t\t",i2
                    # print '\t\t\t\tdef======================================='
                    # for i2 in self.get_def_set(i):
                        # print "\t\t\t\t",i2
                    # print '\t\t\t\tuse========++++++++++++++++=============='
                    # for i2 in self.get_use_set(i):
                        # print "\t\t\t\t",i2
                    # print '\t\t\t\tIN============--------------------======='
                    # for i2 in self.middle_value[1][i][0]:
                        # print "\t\t\t\t",i2
                    # print
                    # print

#For this analysis, we will directly modify the input IR, assign dominance info to them
class DominatorTree():
    def __init__(self, BBLs):
        for b in BBLs:
            for i in b.insts:
                i.dominators = set()
                i.dominatees = set()
                i.idomtors = set()
                i.idomtees = set()
        self.basic_blocks = BBLs
        self.root = self.basic_blocks[0].insts[0]
        self.all_nodes = []
        for b in self.basic_blocks:
            for i in b.insts:
                self.all_nodes += [i]
        for b in self.basic_blocks:
            for i in b.insts:
                i.set_dominators(self.all_nodes)
        self.compute()
        self.compute_idom()

    def compute_idom(self):
        #tmp: {node, current_domtors}
        tmp = {}
        for n in self.all_nodes:
            if n is self.root:
                continue
            tmp[n] = set(n.dominators)
        worklist = [self.root]
        while(len(worklist)>0):
            i_children = []#cur_cur's idomtees
            cur_node = worklist.pop(0)
            for i in tmp:
                remain=set()
                remain = tmp[i] - set([cur_node])
                tmp[i] = remain
                if(i not in worklist and len(remain) ==1):
                    if remain.pop() is i:
                        i_children+=[i]
                    else:
                        assert(False)
            # print cur_node, "my_children:",
            # for x in i_children:print x
            # print "-----------"
            map(lambda x: x.set_idomtees(i_children), [cur_node])
            worklist += list(i_children)

        for i in  self.all_nodes:
            # if(not isinstance(i,codegen.IR) or i.opcode !='jmp'):
                # continue
            if(i.basic_block.label not in ['BBL_5']):
                continue
            # print "...............",i
            # print "idomtors:",len(i.idomtors)
            # print "->",
            # for x in i.idomtors: print x,
            # print ""
            # print "idomtees:",len(i.idomtees)
            # print "->",
            # for x in i.idomtees: print x,
            # print ""
            # print""




    def compute(self):
        worklist = set([self.root])
        while(len(worklist)>0):
            working_node = worklist.pop()
            preds_domtors = [x.dominators for x in working_node.preds]
            new = set([working_node]) | union_sets(preds_domtors)
            if has_change(working_node.dominators,new):
                # print working_node, working_node.basic_block.label,"!!!!!!!!!!!!!!!!!!!!!!!!!"
                # print "old domtors"
                # for x in working_node.dominators:print x
                working_node.set_dominators([])
                working_node.set_dominators(new)
                # print "new domtors"
                # for x in working_node.dominators:print x
                # print "fuck, adding succs: ",
                # for x in working_node.succs:print x
                worklist = worklist | set(working_node.succs)
                # print "****************************************"

        # for b in self.basic_blocks:
            # for i in b.insts:
                # print "...............",i
                # print "domtors:",len(i.dominators)
                # print "->",
                # for x in i.dominators: print x,
                # print ""
                # print "domtees:",len(i.dominatees)
                # print "->",
                # for x in i.dominatees: print x,
                # print ""
                # print""


def union_sets(l_set):
    if len(l_set) == 0:
        return set(l_set)
    return set(reduce(set.intersection, l_set))

def has_change(s1, s2):
    return len(s1^s2) != 0
