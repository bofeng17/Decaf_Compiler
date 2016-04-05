import typecheck
import sys
classtable = {}  # initially empty dictionary of classes.
lastmethod = 0
lastconstructor = 0

# Class table.  Only user-defined classes are placed in the class table.
def lookup(table, key):
    if key in table:
        return table[key]
    else:
        return None

def addtotable(table, key, value):
    table[key] = value


def print_ast():
    for cid in classtable:
        c = classtable[cid]
        c.printout()
    print "-----------------------------------------------------------------------------"

def check_type():
    for cid in classtable:
        c = classtable[cid]
        c.checkMethods()#check T1->S1 T2->S2, T1 strict dominate T2 or vise vesa
        c.resolveType()

def signal_error(etype, rtype, lineno):
    string = 'Type error: expect {0}, but get {1}'.format(etype, rtype)
    print "Line #{1}: {0}".format(string, lineno)
    sys.exit(-1)
def on_error(string, lineno):
    print "Line #{1}: {0}".format(string, lineno)
    sys.exit(-1)

def initialize_ast():
    # define In class:
    cin = Class("In", None)
    cin.builtin = True     # this is a builtin class
    cout = Class("Out", None)
    cout.builtin = True     # this, too, is a builtin class

    scanint = Method('scan_int', cin, 'public', 'static', Type('int'))
    scanint.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanint)

    scanfloat = Method('scan_float', cin, 'public', 'static', Type('float'))
    scanfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanfloat)

    printint = Method('print', cout, 'public', 'static', Type('void'))
    printint.update_body(SkipStmt(None))    # No line number information for the empty body
    printint.add_var('i', 'formal', Type('int'))   # single integer formal parameter
    cout.add_method(printint)

    printfloat = Method('print', cout, 'public', 'static', Type('void'))
    printfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    printfloat.add_var('f', 'formal', Type('float'))   # single float formal parameter
    cout.add_method(printfloat)

    printboolean = Method('print', cout, 'public', 'static', Type('void'))
    printboolean.update_body(SkipStmt(None))    # No line number information for the empty body
    printboolean.add_var('b', 'formal', Type('boolean'))   # single boolean formal parameter
    cout.add_method(printboolean)

    printstring = Method('print', cout, 'public', 'static', Type('void'))
    printstring.update_body(SkipStmt(None))    # No line number information for the empty body
    printstring.add_var('b', 'formal', Type('string'))   # single string formal parameter
    cout.add_method(printstring)

    addtotable(classtable, "In", cin)
    addtotable(classtable, "Out", cout)
    cin.resolveType()
    cout.resolveType()

class Class:
    """A class encoding Classes in Decaf"""
    def __init__(self, classname, superclass):
        self.name = classname
        self.superclass = superclass
        self.fields = {}  # dictionary, keyed by field name
        self.constructors = []
        self.methods = []
        self.builtin = False

    def printout(self):
        if (self.builtin):
            return     # Do not print builtin classes

        print "-----------------------------------------------------------------------------"
        print "Class Name: {0}".format(self.name)
        sc = self.superclass
        if (sc == None):
            scname = ""
        else:
            scname = sc.name
        print "Superclass Name: {0}".format(scname)
        print "Fields:"
        for f in self.fields:
            (self.fields[f]).printout()
        print "Constructors:"
        for k in self.constructors:
            k.printout()
        print "Methods:"
        for m in self.methods:
            m.printout()

    def resolveType(self):
        for k in self.constructors:
            k.resolveType()
        for m in self.methods:
            m.resolveType()

    def checkMethods(self):
        typecheck.check_methods(self.methods)
        typecheck.check_methods(self.constructors)



    def add_field(self, fname, field):
        self.fields[fname] = field
    def add_constructor(self, constr):
        self.constructors.append(constr)
    def add_method(self, method):
        self.methods.append(method)

    def lookup_field(self, fname):
        return lookup(self.fields, fname)


class Type:
    """A class encoding Types in Decaf"""
    def __init__(self, basetype, kind=None, params=None):
        if ((params == None) or (params == 0)):
            if (basetype in ['int', 'boolean', 'float', 'string', 'void', 'error', 'null']):
                self.kind = 'basic'
                self.typename = basetype
            elif (isinstance(basetype, Type)):#use an initialized type to create another Type object
                self.kind = basetype.kind
                if(self.kind == 'array'):
                    self.basetype = basetype.basetype
                else:
                    self.typename = basetype.typename
            else:
                self.kind = kind#(user, class-literal)
                if(kind == None):#these 2 lines is just for compatibility, when it is done should be removed
                    self.kind = 'user'
                self.typename = basetype
        else:
            bt = Type(basetype, params=(params-1))
            self.kind = 'array'
            self.basetype = bt

    def __str__(self):
        if (self.kind == 'array'):
            return 'array(%s)'%(self.basetype.__str__())
        elif (self.kind == 'user' or self.kind == 'class-literal'):
            return 'user(%s)'%(self.typename)
        else:
            return self.typename

    def __repr(self):
        return self.__str__()

class Field:
    """A class encoding fields and their attributes in Decaf"""
    lastfield = 0
    def __init__(self, fname, fclass, visibility, storage, ftype):
        Field.lastfield += 1
        self.name = fname
        self.id = Field.lastfield
        self.inclass = fclass
        self.visibility = visibility
        self.storage = storage
        self.type = ftype

    def printout(self):
        print "FIELD {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.type)

class Method:
    """A class encoding methods and their attributes in Decaf"""
    def __init__(self, mname, mclass, visibility, storage, rtype):
        global lastmethod
        self.name = mname
        lastmethod += 1
        self.id = lastmethod
        self.inclass = mclass
        self.visibility = visibility
        self.storage = storage
        self.rtype = rtype
        self.vars = VarTable()

    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "METHOD: {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.rtype)
        print "Method Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Method Body:"
        self.body.printout()

    def resolveType(self):
        self.body.resolveType()

class Constructor:
    """A class encoding constructors and their attributes in Decaf"""
    def __init__(self, cname, visibility):
        global lastconstructor
        self.name = cname
        lastconstructor += 1
        self.id = lastconstructor
        self.visibility = visibility
        self.vars = VarTable()

    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "CONSTRUCTOR: {0}, {1}".format(self.id, self.visibility)
        print "Constructor Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Constructor Body:"
        self.body.printout()

    def resolveType(self):
        self.body.resolveType()


class VarTable:
    """ Table of variables in each method/constructor"""
    def __init__(self):
        self.vars = {0:{}}
        self.lastvar = 0
        self.lastblock = 0
        self.levels = [0]

    def enter_block(self):
        self.lastblock += 1
        self.levels.insert(0, self.lastblock)
        self.vars[self.lastblock] = {}

    def leave_block(self):
        self.levels = self.levels[1:]
        # where should we check if we can indeed leave the block?

    def add_var(self, vname, vkind, vtype):
        self.lastvar += 1
        c = self.levels[0]   # current block number
        v = Variable(vname, self.lastvar, vkind, vtype)
        vbl = self.vars[c]  # list of variables in current block
        vbl[vname] = v

    def _find_in_block(self, vname, b):
        if (b in self.vars):
            # block exists
            if (vname in self.vars[b]):
                return self.vars[b][vname]
        # Otherwise, either block b does not exist, or vname is not in block b
        return None

    def find_in_current_block(self, vname):
        return self._find_in_block(vname, self.levels[0])

    def find_in_scope(self, vname):
        for b in self.levels:
            v = self._find_in_block(vname, b)
            if (v != None):
                return v
            # otherwise, locate in enclosing block until we run out
        return None

    def get_params(self):
        outermost = self.vars[0]  # 0 is the outermost block
        ids = [outermost[vname].id for vname in outermost if outermost[vname].kind=='formal']
        return ids

    def get_params_types(self):
        outermost = self.vars[0]  # 0 is the outermost block
        types = [outermost[vname].type for vname in outermost if outermost[vname].kind=='formal']
        return types

    def printout(self):
        print "Variable Table:"
        for b in range(self.lastblock+1):
            for vname in self.vars[b]:
                v = self.vars[b][vname]
                v.printout()


class Variable:
    """ Record for a single variable"""
    def __init__(self, vname, id, vkind, vtype):
        self.name = vname
        self.id = id
        self.kind = vkind
        self.type = vtype

    def printout(self):
        print "VARIABLE {0}, {1}, {2}, {3}".format(self.id, self.name, self.kind, self.type)
    def resolveType(self):
        self.expr_type = self.type
        print "Variable type @@@@"

#Statements only have synthetic type: "Correct" or "Wrong"
#the resolveType() function will have 2 results
#1) the return value indicate the synthetic type
#2) all the expr components of the stmt will have their "type of class Type" field filled up
class Stmt(object):
    """ Top-level (abstract) class representing all statements"""

class IfStmt(Stmt):
    def __init__(self, condition, thenpart, elsepart, lines):
        self.lines = lines
        self.condition = condition
        self.thenpart = thenpart
        self.elsepart = elsepart

    def printout(self):
        print "If(",
        self.condition.printout()
        print ", ",
        self.thenpart.printout()
        print ", ",
        self.elsepart.printout()
        print ")"

    def resolveType(self):
        self.stmttype = 'Wrong'#store the 'synthetic sugar type in case we need it in the future'
        condtype = self.condition.resolveType()
        thentype = self.thenpart.resolveType()
        elsetype = self.elsepart.resolveType()
        cond = self.condition.expr_type
        if (condtype == 'Correct' and \
            thentype == 'Correct' and \
            elsetype == 'Correct'):
            if(cond.typename == 'boolean'):
                self.stmttype = 'Correct'
            else:
                signal_error('boolean', cond.typename, self.lines)
        return self.stmttype

class WhileStmt(Stmt):
    def __init__(self, cond, body, lines):
        self.lines = lines
        self.cond = cond
        self.body = body

    def printout(self):
        print "While(",
        self.cond.printout()
        print ", ",
        self.body.printout()
        print ")"

    def resolveType(self):
        self.stmttype = 'Wrong'#store the 'synthetic sugar type in case we need it in the future'
        condtype = self.cond.resolveType()
        bodytype = self.body.resolveType()
        cond = self.cond.expr_type
        if (condtype == 'Correct' and \
            bodytype == 'Correct'):
            if(cond.typename == 'boolean'):
                self.stmttype = 'Correct'
            else:
                signal_error('boolean', cond.typename, self.lines)
        return self.stmttype



class ForStmt(Stmt):
    def __init__(self, init, cond, update, body, lines):
        self.lines = lines
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body

    def printout(self):
        print "For(",
        if (self.init != None):
            self.init.printout()
        print ", ",
        if (self.cond != None):
            self.cond.printout()
        print ", ",
        if (self.update != None):
            self.update.printout()
        print ", ",
        self.body.printout()
        print ")"

    def resolveType(self):
        self.stmttype = 'Wrong'#store the 'synthetic sugar type in case we need it in the future'
        condtype = self.cond.resolveType()
        inittype = self.init.resolveType()
        updatetype = self.update.resolveType()
        bodytype = self.body.resolveType()
        cond = self.cond.expr_type
        if (condtype == 'Correct' and \
            inittype == 'Correct' and \
            updatetype == 'Correct' and \
            bodytype == 'Correct'):
            if(cond.typename == 'boolean'):
                self.stmttype = 'Correct'
            else:
                signal_error('boolean', cond.typename, self.lines)
        return self.stmttype

class ReturnStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr

    def printout(self):
        print "Return(",
        if (self.expr != None):
            self.expr.printout()
        print ")"

    def updateMethod(self, methodref):
        self.methodref = methodref

    def resolveType(self):
        self.stmttype = 'Wrong'#store the 'synthetic sugar type in case we need it in the future'
        rtype = self.methodref.rtype#Type obj
        if (self.expr == None):
            if (rtype.kind == 'basic' and rtype.typename == 'void'):
                self.stmttype = 'Correct'
        else:
            rettype = self.expr.resolveType()
            exprtype = self.expr.expr_type;#Type obj
            if(rettype == 'Correct' and typecheck.is_subtype(exprtype, rtype)):
                self.stmttype = 'Correct'

        if(self.stmttype == 'Wrong'):
            signal_error(rtype, exprtype, self.lines)
        return self.stmttype





class BlockStmt(Stmt):
    def __init__(self, stmtlist, lines):
        self.lines = lines
        self.stmtlist = [s for s in stmtlist if (s != None) and (not isinstance(s, SkipStmt))]

    def printout(self):
        print "Block(["
        if (len(self.stmtlist) > 0):
            self.stmtlist[0].printout()
        for s in self.stmtlist[1:]:
            print ", ",
            s.printout()
        print "])"
    def resolveType(self):
        self.stmttype = 'Correct'
        for s in self.stmtlist:
            if(s.resolveType()=='Wrong'):
                self.stmttype = 'Wrong'
                break
        return self.stmttype


class BreakStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Break"

    def resolveType():
        return 'Correct'
class ContinueStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Continue"
    def resolveType():
        return 'Correct'

class ExprStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr

    def printout(self):
        print "Expr(",
        self.expr.printout()
        print ")"

    def resolveType(self):
        self.stmttype = 'Wrong'
        if(self.expr.resolveType() == 'Correct'):
            self.stmttype = 'Correct'
        return self.stmttype

class SkipStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Skip"
    def resolveType(self):
        return 'Correct'



#For expressions, the resolveType function will have two results
#1) the return value indicate the synthetic type of the expr, "Correct" or "Wrong"
#2) each expr will have a "type" field, indicate the concret type of this expr
class Expr(object):
    def __repr__(self):
        return "Unknown expression"
    def printout(self):
        print self,


class ConstantExpr(Expr):
    def __init__(self, kind, arg=None, lines=None):
        self.lines = lines
        self.kind = kind
        if (kind=='int'):
            self.int = arg
        elif (kind == 'float'):
            self.float = arg
        elif (kind == 'string'):
            self.string = arg


    def __repr__(self):
        s = "Unknown"
        if (self.kind == 'int'):
            s = "Integer-constant(%d)"%self.int
        elif (self.kind == 'float'):
            s = "Float-constant(%g)"%self.float
        elif (self.kind == 'string'):
            s = "String-constant(%s)"%self.string
        elif (self.kind == 'Null'):
            s = "Null"
        elif (self.kind == 'True'):
            s = "True"
        elif (self.kind == 'False'):
            s = "False"
        return "Constant({0})".format(s)

    def resolveType(self):
        if(self.kind in ['int', 'float', 'string']):
            self.expr_type = Type(self.kind)
        if(self.kind in ['True', 'False']):
            self.expr_type = Type('boolean')
        if(self.kind == 'Null'):
            self.expr_type = Type('null')
        return 'Correct'

class VarExpr(Expr):
    def __init__(self, var, lines):
        self.lines = lines
        self.var = var# Variable obj
        self.expr_type = var.type
    def __repr__(self):
        return "Variable(%d)"%self.var.id
    def resolveType(self):
        self.expr_type = self.var.type
        return 'Correct'

class UnaryExpr(Expr):
    def __init__(self, uop, expr, lines):
        self.lines = lines
        self.uop = uop
        self.arg = expr
    def __repr__(self):
        return "Unary({0}, {1})".format(self.uop, self.arg)
    def resolveType(self):
        if (self.expr.resolveType() == 'Correct'):
            resolved_type = self.expr.expr_type
            if(self.uop == 'uminus'):
                if(resolved_type.typename in ['int', 'float']):
                    self.expr_type = resolved_type
                    return 'Correct'
                else:
                    signal_error('int or float', resolved_type.typename, self.lines)
            if(self.uop == 'neg'):
                if(resolved_type.typename == 'boolean'):
                    self.expr_type = resolved_type
                    return 'Correct'
                else:
                    signal_error('boolean', resolved_type.typename, self.lines)

        self.expr_type = Type('error')
        return 'Wrong'


class BinaryExpr(Expr):
    def __init__(self, bop, arg1, arg2, lines):
        self.lines = lines
        self.bop = bop
        self.arg1 = arg1
        self.arg2 = arg2
    def __repr__(self):
        return "Binary({0}, {1}, {2})".format(self.bop,self.arg1,self.arg2)
    def resolveType(self):
        if(self.arg1.resolveType() == 'Correct' and self.arg2.resolveType() == 'Correct'):
            arg1_type = self.arg1.expr_type
            arg2_type = self.arg2.expr_type
            if(self.bop in ['add','sub','mul','div']):
                if(arg1_type.typename=='int' and arg2_type.typename=='int'):
                    self.expr_type = Type('int')
                    return 'Correct'
                elif(arg1_type.typename=='float' or arg2_type.typename=='float'):
                    self.expr_type = Type('float')
                    return 'Correct'
                else:
                    signal_error('int/float', arg1_type.typename+'/'+arg2_type.typename, self.lines)

            if(self.bop in ['and','or']):
                if(arg1_type.typename=='boolean' and arg2_type.typename=='boolean'):
                    self.expr_type = Type('boolean')
                    return 'Correct'
                else:
                    signal_error('boolean/boolean', arg1_type.typename+'/'+arg2_type.typename, self.lines)

            if(self.bop in ['lt','leq','gt','geq']):
                if(arg1_type.typename in ['int','float'] or arg2_type.typename in ['int','float']):
                    self.expr_type = Type('boolean')
                    return 'Correct'
                else:
                    signal_error('int/float', arg1_type.typename+'/'+arg2_type.typename, self.lines)

            if(self.bop in ['eq','neq']):
                if(typecheck.is_subtype(arg1_type, arg2_type) or \
                   typecheck.is_subtype(arg2_type, arg1_type)):
                    self.expr_type = Type('boolean')
                    return 'Correct'

        self.expr_type = Type('error')
        return 'Wrong'

class AssignExpr(Expr):
    def __init__(self, lhs, rhs, lines):
        self.lines = lines
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self):
        return "Assign({0}, {1}, {2}, {3})".format(self.lhs, self.rhs, self.lhs.expr_type, self.rhs.expr_type)


    def resolveType(self):
        if(self.lhs.resolveType() == 'Correct' and self.rhs.resolveType() == 'Correct'):
            if(typecheck.is_subtype(self.rhs.expr_type, self.lhs.expr_type)):
                self.expr_type = self.rhs.expr_type#TODO: verify there is no need to alloc a new type
                return 'Correct'
            else:
                on_error("rhs's type:{0} is not a subtype of lhs's type:{1}".format(self.rhs.expr_type, self.lhs.expr_type), self.lines)
        self.expr_type = Type('error')
        return 'Wrong'



class AutoExpr(Expr):
    def __init__(self, arg, oper, when, lines):
        self.lines = lines
        self.arg = arg
        self.oper = oper
        self.when = when
    def __repr__(self):
        return "Auto({0}, {1}, {2})".format(self.arg, self.oper, self.when)
    def resolveType(self):
        if(self.arg.resolveType() == 'Correct'):
            if(self.arg.expr_type.typename in ['int','float']):
                self.expr_type = self.arg.expr_type#TODO: verify there is no need to alloc a new type
                return 'Correct'
            else:
                signal_error('int/float',self.arg.expr_type.typename, self.lines)
        self.expr_type = Type('error')
        return 'Wrong'


class FieldAccessExpr(Expr):
    def __init__(self, base, fname, lines):
        self.lines = lines
        self.base = base
        self.fname = fname
    def __repr__(self):
        return "Field-access({0}, {1}, {2})".format(self.base, self.fname, self.resolved_field.id)
    def updateClass(self, containingCls):
        self.containingCls = containingCls
    def resolveType(self):
        if(self.base.resolveType() == 'Correct'):
            base_type = self.base.expr_type
            target_cls = lookup(classtable, base_type.typename)#the class to start looking at(obj or static)
            accessing_cls = self.containingCls
            if(base_type.kind == 'user'):
                            #(target_cls,accessing_cls,field_name,static=False)
                self.resolved_field = typecheck.resolve_field(target_cls, accessing_cls, self.fname,False)
            if(base_type.kind == 'class-literal'):
                            #(target_cls,accessing_cls,field_name,static=True)
                self.resolved_field = typecheck.resolve_field(target_cls, accessing_cls, self.fname,True)
            if(self.resolved_field!=None):
                self.expr_type = self.resolved_field.type
                return 'Correct'
            else:
                on_error("Can't resolve field: {0}.{1} please check the visibility and storage types of intended field to call ".format(base_type.typename,self.fname), self.lines)
        self.expr_type = Type('error')
        return 'Wrong'




class MethodInvocationExpr(Expr):
    def __init__(self, field, args, lines):
        self.lines = lines
        self.base = field.base
        self.mname = field.fname
        self.args = args#[expr_arg1, expr_arg2, expr_arg3,...]
    def __repr__(self):
        return "Method-call({0}, {1}, {2},{3})".format(self.base, self.mname, self.args, self.resolved_meth.id)
    def updateClass(self, containingCls):
        self.containingCls = containingCls
    def resolveType(self):
        if(self.base.resolveType() == 'Correct'):
            args_ok = True
            for arg in self.args:
                if(arg.resolveType() != 'Correct'):
                    args_ok = False
                    break
            if(args_ok):
                base_type = self.base.expr_type
                #the class to start looking at
                target_cls = lookup(classtable, base_type.typename)
                accessing_cls = self.containingCls
                if(base_type.kind == 'user'):
                    #(target_cls,accessing_cls,meth_name,args(type resolved),static=False)
                    self.resolved_meth = typecheck.resolve_method(target_cls, accessing_cls, self.mname,self.args,False)
                if(base_type.kind == 'class-literal'):
                    #(target_cls,accessing_cls,meth_name,args(type resolved),static=True)
                    self.resolved_meth = typecheck.resolve_method(target_cls, accessing_cls, self.mname,self.args,True)
                if(self.resolved_meth!=None):
                    self.expr_type = self.resolved_meth.rtype
                    return 'Correct'
                else:
                    on_error("Can't resolve method: {0}, please check the visibility and storage types of the intended method to call".format(self.mname), self.lines)
        self.expr_type = Type('error')
        return 'Wrong'

class NewObjectExpr(Expr):
    def __init__(self, cref, args, lines):
        self.lines = lines
        self.classref = cref
        self.args = args
    def updateClass(self, containingCls):
        self.containingCls = containingCls
    def __repr__(self):
        return "New-object({0},{1},{2})".format(self.classref.name, self.args, self.resolved_ctor.id)
    def resolveType(self):
        args_ok = True
        for arg in self.args:
            if(arg.resolveType() != 'Correct'):
                args_ok = False
                break
        if(args_ok):
            target_cls = self.classref
            accessing_cls = self.containingCls
            #(target_cls,accessing_cls,args(type resolved))
            self.resolved_ctor = typecheck.resolve_ctor(target_cls, accessing_cls, self.args)
            if(self.resolved_ctor != None):
                self.expr_type = Type(target_cls.name, 'user')
                return 'Correct'
            else:
                on_error("Can't resolve CONSTRUCTOR for new object: {0}, please check the visibility constructors ".format(self.classref.name), self.lines)
        self.expr_type = Type('error')
        return 'Wrong'


class ThisExpr(Expr):
    def __init__(self, lines):
        self.lines = lines
    def __repr__(self):
        return "This"
    def updateClass(self, containingCls):
        self.containingCls = containingCls
    def resolveType(self):
        self.expr_type = Type(self.containingCls.name, 'user')
        return 'Correct'

class SuperExpr(Expr):
    def __init__(self, lines):
        self.lines = lines
    def __repr__(self):
        return "Super"
    def updateClass(self, containingCls):
        self.containingCls = containingCls
    def resolveType(self):
        parentCls = self.containingCls.superclass
        if(parentCls != None):
            self.expr_type = Type(parentCls.name, 'user')
            return 'Correct'
        self.expr_type = Type('error')
        return 'Wrong'


class ClassReferenceExpr(Expr):
    def __init__(self, cref, lines):
        self.lines = lines
        self.classref = cref
    def __repr__(self):
        return "ClassReference({0})".format(self.classref.name)
    def resolveType(self):
        self.expr_type = Type(self.classref.name, 'class-literal')
        return 'Correct'


class ArrayAccessExpr(Expr):#the process of derefence--peel off array(T) and get T
    def __init__(self, base, index, lines):
        self.lines = lines
        self.base = base
        self.index = index
    def __repr__(self):
        return "Array-access({0}, {1})".format(self.base, self.index)
    def resolveType(self):
        if(self.base.resolveType() == 'Correct' and self.index.resolveType() == 'Correct'):
            base_type = self.base.expr_type
            index_type = self.index.expr_type
            if(base_type.kind == 'array' and index_type.typename == 'int'):
                self.expr_type = base_type.basetype#TODO: verify no need to alloc a new type
                return 'Correct'
        self.expr_type = Type('error')
        return 'Wrong'



class NewArrayExpr(Expr):
    def __init__(self, basetype, args, lines):
        self.lines = lines
        self.basetype = basetype#already built during ast construction
        self.args = args#sequence of dim_expr
    def __repr__(self):
        return "New-array({0}, {1})".format(self.basetype, self.args)
    def resolveType(self):
        dim_expr_ok = True
        for d in self.args:
            resolve_ok = d.resolveType()
            t = d.expr_type
            if(resolve_ok != 'Correct' or t.typename != 'int'):
                dim_expr_ok = False
                break
        if(dim_expr_ok):
            dim_expr_len = len(self.args)
            self.expr_type = Type(self.basetype, params=dim_expr_len)#combine dim_star and dim_expr's dimensions
            return 'Correct'
        self.expr_type = Type('error')
        return 'Wrong'




