#IN and OUT and gen and kill have element type IR
#results: {BB,INs}
#middle_value: [converged, {BB, [INs,OUTs]}]
class ReachingDef():
    def __init__(self, BBLs):
        self.basic_blocks = BBLs
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
        return set([x for x in b.insts if len(x.get_def())>0])
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
#TODO, comment this out, dont'delete
            if(bb.label=='BBL_9' and False):
                print '\t\t\t\tIN============--------------------======='
                for i in self.middle_value[1][bb][0]:
                    print "\t\t\t\t",i.basic_block.label, i
                print '\t\t\t\tKILL======================================='
                for i in self.get_kill_set(bb):
                    print "\t\t\t\t",i.basic_block.label, i
                print '\t\t\t\tGEN========++++++++++++++++=============='
                for i in self.get_gen_set(bb):
                    print "\t\t\t\t",i.basic_block.label, i
                print '\t\t\t\tOUT=====***************************======='
                for i in self.middle_value[1][bb][1]:
                    print "\t\t\t\t",i.basic_block.label, i

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






class Liveness():
    def __init__(self, BBLs):
        self.basic_blocks = BBLs

    def get_INs(self, ir):
        pass
    def compute(self):
        pass

def has_change(s1, s2):
    return len(s1^s2) != 0
