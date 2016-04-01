classtable = {}  # initially empty dictionary of classes. {class_name: Class object, ...}
lastmethod = 0
lastconstructor = 0

# Class table.  Only user-defined classes are placed in the class table.
def lookup(table, key):
    if key in table:
        return table[key]
    else:
        return None

def addtotable(table, key, value):
    table[key] = value # the order in dict differs than that in list


def print_ast():
    for cid in classtable:
        c = classtable[cid]
        c.printout()
    print "-----------------------------------------------------------------------------"

def trav_ast():
    for cid in classtable:
        c = classtable[cid]
        c.trav()
    print "-----------------------------------------------------------------------------"

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


class Class:
    """A class encoding Classes in Decaf"""
    def __init__(self, classname, superclass):
        self.name = classname
        self.superclass = superclass # None or class object
        self.fields = {}  # dictionary, keyed by field name
        self.constructors = []
        self.methods = []
        self.builtin = False

    def trav(self):
        for f in self.fields:
            (self.fields[f]).trav()
        print "Constructors:"
        for k in self.constructors:
            k.trav()
        print "Methods:"
        for m in self.methods:
            m.trav()

    def printout(self):
        if (self.builtin):
            return     # Do not print builtin methods

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
    def __init__(self, basetype, kind = None, params=None):
        if ((params == None) or (params == 0)): # None for basic type, 0 for recursive exit point of array type
            # Elementary type
            if basetype in ['int', 'float', 'boolean', 'string', 'void', 'null', 'error', 'correct']: # 'correct' for stmt
                # built-in type
                self.kind = 'elementary'
                self.typename = basetype # build-in type name
            elif kind in ['user', 'class-literal', 'tuple']:
                # user-defined type/class-literal type
                self.kind = kind
                # self.typename:
                # class_name if kind == 'user' or 'class-literal'
                # list of Type if kind == 'tuple'
                self.typename = basetype
            elif (isinstance(basetype, Type)):
                # copy from Type
                self.kind = basetype.kind
                self.typename = basetype.typename
            else:
                print "Undefined type!"
        else:
            # Array type
            bt = Type(basetype, params=params-1)
            self.kind = 'array'
            self.typename = bt # Type that is stripped of one level of 'array'

    @staticmethod
    def is_subtype(a, b):
        # return (True, diff) if tuple Type a is sub-type of b
        # TODO: verify diff value
        diff = 0
        # rule 1
        if a == b:
            return True, 0

        # rule 4/6
        if a.typename == 'null' and b.kind in ['user', 'class-literal']:
            # TODO: diff=1 reasonable?
            return True, 1

        if a.kind == b.kind:
            # rule 2
            if a.typename == 'int' and b.typename == 'float':
                return True, 1
            # rule 3/7
            if a.kind in ['user', 'class-literal']:
                # if a is subclass of b
                cls = lookup(classtable, a.typename)
                while cls is not None:
                    if cls.name == b.typename:
                        return (True, diff)
                    cls = cls.superclass
                    diff += 1
            elif a.kind == 'tuple':
                if len(a.typename) == len(b.typename):
                    for (aa, bb) in zip(a, b):
                        (is_sub, cur_diff) = Type.is_subtype(aa, bb)
                        if not is_sub:
                            break
                        diff += cur_diff
                    return True, diff
            # rule 5
            elif a.kind == 'array':
                return Type.is_subtype(a.typename, b.typename)

        return False, 2**30

    def __eq__(self, other):
        if isinstance(other, Type):
            if self.kind == other.kind and self.typename == other.typename:
                return True
        return False

    def __str__(self):
        if (self.kind == 'array'):
            return 'array(%s)'%(self.typename.__str__())
        elif (self.kind == 'user'):
            return 'user(%s)'%(self.typename)
        elif (self.kind == 'class-literal'):
            return 'class-literal(%s)'%(self.typename)
        else:
            # Elementary type
            return self.typename
        # TODO: do we need print tuple?

    def __repr__(self):
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

    def trav(self):
        pass # stub for code emission

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

    def update_formal_type(self, formal_sign): # formal_sgin: tuple Type for formal_sign
        self.formal_type = Type(formal_sign)

    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def trav(self):
        self.body.trav()

    def printout(self):
        print "METHOD: {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.rtype)
        print "Method Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Method Body:"
        self.body.printout()

class Constructor:
    """A class encoding constructors and their attributes in Decaf"""
    def __init__(self, cname, visibility):
        global lastconstructor
        self.name = cname
        lastconstructor += 1
        self.id = lastconstructor
        self.visibility = visibility
        self.vars = VarTable()

    def update_formal_type(self, formal_sign): # formal_sgin: tuple Type for formal_sign
        self.formal_type = Type(formal_sign)

    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def trav(self):
        self.body.trav()

    def printout(self):
        print "CONSTRUCTOR: {0}, {1}".format(self.id, self.visibility)
        print "Constructor Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Constructor Body:"
        self.body.printout()


class VarTable:
    """ Table of variables in each method/constructor"""
    def __init__(self):
        self.vars = {0:{}}
        self.lastvar = 0
        self.lastblock = 0 # unique block "id" in current VarTable
        self.levels = [0] # stack, [curBlckId, ..., topLevBlckId(i.e.0)]

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

    def trav(self):
        pass # should we do anything?

    def printout(self):
        print "VARIABLE {0}, {1}, {2}, {3}".format(self.id, self.name, self.kind, self.type)


class Stmt(object):
    """ Top-level (abstract) class representing all statements"""

class IfStmt(Stmt):
    def __init__(self, condition, thenpart, elsepart, lines):
        self.lines = lines
        self.cond = condition
        self.thenpart = thenpart
        self.elsepart = elsepart

    def trav(self):
        self.cond.trav()
        self.thenpart.trav()
        self.elsepart.trav()

        if self.cond == Type('boolean') and self.thenpart.type != Type('error') and \
                        self.elsepart.type != Type('error'):
            self.stmt_type = Type('correct')
        else:
            self.stmt_type = Type('error')

    def printout(self):
        print "If(",
        self.cond.printout()
        print ", ",
        self.thenpart.printout()
        print ", ",
        self.elsepart.printout()
        print ")"

class WhileStmt(Stmt):
    def __init__(self, cond, body, lines):
        self.lines = lines
        self.cond = cond
        self.body = body

    def trav(self):
        self.cond.trav()
        self.body.trav()

        if self.cond == Type('boolean') and self.body.type != Type('error'):
            self.stmt_type = Type('correct')
        else:
            self.stmt_type = Type('error')

    def printout(self):
        print "While(",
        self.cond.printout()
        print ", ",
        self.body.printout()
        print ")"

class ForStmt(Stmt):
    def __init__(self, init, cond, update, body, lines):
        self.lines = lines
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body

    def trav(self):
        self.init.trav()
        self.cond.trav()
        self.update.trav()
        self.body.trav()

        if self.init.type != Type('error') and self.cond.type == Type('boolean') and \
            self.update.type != Type('error') and self.body.type != Type('error'):
            self.stmt_type = Type('correct')
        else:
            self.stmt_type = Type('error')

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

class ReturnStmt(Stmt):
    def __init__(self, expr, containing_method, lines):
        self.lines = lines
        self.expr = expr
        self.containing_method = containing_method # can be either method/ctro

    def trav(self):
        self.stmt_type = Type('error')
        if self.expr:
            # return expr;
            self.expr.trav()
            if isinstance(self.containing_method, Method):
                if self.containing_method.rtype == self.expr.type:
                    self.stmt_type = Type('correct')
        else:
            # return;
            if isinstance(self.containing_method, Method):
                # method
                if self.containing_method.rtype == Type('void'):
                    self.stmt_type = Type('correct')
            else:
                # ctor
                self.stmt_type = Type('correct')

    def printout(self):
        print "Return(",
        if (self.expr != None):
            self.expr.printout()
        print ")"

class BlockStmt(Stmt):
    def __init__(self, stmtlist, lines):
        self.lines = lines
        self.stmtlist = [s for s in stmtlist if (s != None) and (not isinstance(s, SkipStmt))]

    def trav(self):
        type_correct = True
        for s in self.stmtlist:
            s.trav()
            if s.trav() == Type('error'):
                type_correct = False
                break
        self.stmt_type = Type('correct') if type_correct else Type('error')

    def printout(self):
        print "Block(["
        if (len(self.stmtlist) > 0):
            self.stmtlist[0].printout()
        for s in self.stmtlist[1:]:
            print ", ",
            s.printout()
        print "])"

class BreakStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def trav(self):
        self.stmt_type = Type('correct')

    def printout(self):
        print "Break"

class ContinueStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def trav(self):
        self.stmt_type = Type('correct')

    def printout(self):
        print "Continue"

class ExprStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr

    def trav(self):
        self.expr.trav()

        self.stmt_type = Type('correct') if self.expr.type != Type('error') else Type('error')

    def printout(self):
        print "Expr(",
        self.expr.printout()
        print ")"

class SkipStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def trav(self):
        self.stmt_type = Type('correct')

    def printout(self):
        print "Skip"


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

    def trav(self):
        if (self.kind == 'Null'):
            self.type = Type('null')
        elif self.kind in ['True', 'False']:
            self.type = Type('boolean')
        else: # int, float, string
            self.type = Type(self.kind)

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

class VarExpr(Expr):
    def __init__(self, var, lines):
        self.lines = lines
        self.var = var

    def trav(self):
        self.var.trav()
        self.type = self.var.type

    def __repr__(self):
        return "Variable(%d)"%self.var.id

class UnaryExpr(Expr):
    def __init__(self, uop, expr, lines):
        self.lines = lines
        self.uop = uop
        self.arg = expr

    def trav(self):
        self.uop.trav()
        self.arg.trav()

        if self.uop == 'uminus':
            self.type = self.arg.type if self.arg.type in [Type('int'), Type('float')] else Type('error')
        else: # 'neg'
            self.type = self.arg.type if self.arg.type == Type('boolean') else Type('error')

    def __repr__(self):
        return "Unary({0}, {1})".format(self.uop, self.arg)

class BinaryExpr(Expr):
    def __init__(self, bop, arg1, arg2, lines):
        self.lines = lines
        self.bop = bop
        self.arg1 = arg1
        self.arg2 = arg2

    def trav(self):
        self.arg1.trav()
        self.arg2.trav()

        # propagate type
        self.type = Type('error')
        if self.bop in ['+', '-', '*', '/']:
            if self.arg1.type == Type('int') and self.arg2.type == Type('int'):
                self.type = Type('int')
            elif self.arg1.type in [Type('int'), Type('float')] and self.arg2.type in [Type('int'), Type('float')]:
                self.type = Type('float')
        elif self.bop in ['&&', '||']:
            if self.arg1.type == Type('boolean') and self.arg2.type == Type('boolean'):
                self.type = Type('boolean')
        elif self.bop in ['<', '<=', '>', '>=']:
            if self.arg1.type in [Type('int'), Type('float')] and self.arg2.type in [Type('int'), Type('float')]:
                self.type = Type('boolean')
        else: # ['==', '!=']
            if self.arg1.type.is_subtype(self.arg2.type) or self.arg2.type.is_subtype(self.arg1.type):
                self.type = Type('boolean')

    def __repr__(self):
        return "Binary({0}, {1}, {2})".format(self.bop,self.arg1,self.arg2)

class AssignExpr(Expr):
    def __init__(self, lhs, rhs, lines):
        self.lines = lines
        self.lhs = lhs
        self.rhs = rhs

    def trav(self):
        self.lhs.trav()
        self.rhs.trav()

        if (self.lhs.type != 'error' and self.rhs.type != 'error') and \
            self.rhs.type.is_subtype(self.lhs.type):
            self.type = self.rhs.type # TODO: self.rhs.type or self.lhs.type?
        else:
            self.type = Type('error')

    def __repr__(self):
        return "Assign({0}, {1}, {2}, {3})".format(self.lhs, self.rhs, self.lhs.type, self.rhs.type)


class AutoExpr(Expr):
    def __init__(self, arg, oper, when, lines):
        self.lines = lines
        self.arg = arg
        self.oper = oper
        self.when = when

    def trav(self):
        self.arg.trav()

        self.type = self.arg.type if self.arg.type in \
                                     [Type('int'), Type('float')] else Type('error')

    def __repr__(self):
        return "Auto({0}, {1}, {2})".format(self.arg, self.oper, self.when)

class FieldAccessExpr(Expr):
    def __init__(self, base, fname, containing_cls, lines):
        self.lines = lines
        self.type = None # resolved by name resolution
        self.field_id = None # resolved by name resolution
        self.base = base
        self.fname = fname
        self.containing_cls = containing_cls

    def resolve_name(self):
        # find start class for searching, and set storage
        storage = 'instance'
        if isinstance(self.base, ThisExpr):
            cls = self.containing_cls
        elif isinstance(self.base, SuperExpr):
            cls = self.containing_cls.superclass
        elif isinstance(self.base, NewObjectExpr):
            cls = self.base.classref
        elif isinstance(self.base, ClassReferenceExpr):
            cls = self.base.classref
            storage = 'static'
        else:
            # TODO: This branch should never execute
            print self.lines + ': Unrecognized base type for MethodInvocationExpr'
            return False

        # find candidate and test it
        while cls is not None:
            if self.fname in cls.fields: # differs than cls.methods, cls.fields is dict
                field = cls.fields[self.name]
                if storage == field.storage and \
                        (field.visibility == 'public' or cls == self.containing_cls):
                    self.field_id = field.id
                    self.type = field.rtype
                    return True
            cls = cls.superclass
        return False

    def trav(self):
        # TODO: really need explicit traverse for self.base?
        self.base.trav()

        if isinstance(self.base, FieldAccessExpr):
            # Now it's sure self.base is real Field access (cannot be method_invocation)
            # so resolve name for it
            # Cautious! call self.base.resolve_name() instead of self.resolve_name()
            # leave self.type unresolved because it may be real Field access or method_invocation
            if not self.base.resolve_name():
                # self.type is already set if self.resolve_name() is True
                self.type = Type('error')

    def __repr__(self):
        return "Field-access({0}, {1}, {2})".format(self.base, self.fname, self.field_id)

class MethodInvocationExpr(Expr):
    def __init__(self, field, args, containing_cls, lines):
        self.lines = lines
        self.type = None # resolved by name resolution
        self.method_id = None # resolved by name resolution
        # FieldAccessExpr is broken down into two parts: base & mname
        self.base = field.base # ThisExpr/SuperExpr/NewObjectExpr/ClassReferenceExpr
        self.mname = field.fname # method name
        self.args = args # [expr1, expr2, ...]
        self.containing_cls = containing_cls # Class object

    def resolve_name(self):
        param_type = []
        for arg in self.args:
            param_type.append(arg.type)
        param_sign = Type(param_type) # signature of param passed into

        # find start class for searching, and set storage
        storage = 'instance'
        if isinstance(self.base, ThisExpr):
            cls = self.containing_cls
        elif isinstance(self.base, SuperExpr):
            cls = self.containing_cls.superclass
        elif isinstance(self.base, NewObjectExpr):
            cls = self.base.classref
        elif isinstance(self.base, ClassReferenceExpr):
            cls = self.base.classref
            storage = 'static'
        else:
            # TODO: This branch should never execute
            print self.lines + ': Unrecognized base type for MethodInvocationExpr'
            return False

        # find candidate and test it
        found = False
        min_diff = 2**30 # set to an arbitrarily large number
        while cls is not None:
            for method in cls.methods:
                if self.mname == method.name and storage == method.storage and \
                        (method.visibility == 'public' or cls == self.containing_cls):
                    (is_sub, total_diff) = Type.is_subtype(param_sign, method)
                    if is_sub:
                        found = True
                        if total_diff < min_diff:
                            min_diff = total_diff
                            self.method_id = method.id
                            self.type = method.rtype
            if found:
                return True
            cls = cls.superclass
        return False

    def trav(self):
        self.base.trav()
        # must firstly decorate subtree of self.args with type info
        for arg in self.args:
            arg.trav()

        # then do name resolution with type info of self.args
        if not self.resolve_name():
            # self.type is already set if self.resolve_name() is True
            self.type = Type('error')

    def __repr__(self):
        return "Method-call({0}, {1}, {2}, {3})".format(self.base, self.mname, self.args, self.method_id)



class NewObjectExpr(Expr):
    def __init__(self, cref, args, containing_cls, lines):
        self.lines = lines
        self.type = None # resolved by name resolution
        self.ctor_id = None # resolved by name resolution
        self.classref = cref # Class object, cannot be None
        self.args = args
        self.containing_cls = containing_cls # Class object
    # called when AST is traversed for NameResolution purpose
    def resolve_name(self):
        param_type = []
        for arg in self.args:
            param_type.append(arg.type)
        param_sign = Type(param_type) # signature of param passed into

        # find candidate and test it
        cls = self.classref
        found = False
        min_diff = 2**30 # set to an arbitrarily large number
        while cls is not None:
            for ctor in cls.constructors:
                if ctor.visibility == 'public' or cls == self.containing_cls:
                    (is_sub, total_diff) = Type.is_subtype(param_sign, ctor)
                    if is_sub:
                        found = True
                        if total_diff < min_diff:
                            min_diff = total_diff
                            self.ctor_id = ctor.id
                            self.type = Type(self.classref.name, kind='user')
            if found:
                return True
            cls = cls.superclass
        return False

    def trav(self):
        # must firstly decorate subtree of self.args with type info
        self.args.trav()

        # then do name resolution with type info of self.args
        if not self.resolve_name():
            # self.type is already set if self.resolve_name() is True
            self.type = Type('error')

    def __repr__(self):
        return "New-object({0}, {1}, {2})".format(self.classref.name, self.args, self.ctor_id)

class ThisExpr(Expr):
    def __init__(self, containing_cls, lines):
        self.lines = lines
        self.containing_cls = containing_cls

    def trav(self):
        self.type = Type(self.containing_cls, 'user')

    def __repr__(self):
        return "This"

class SuperExpr(Expr):
    def __init__(self, containing_cls, lines):
        self.lines = lines
        self.containing_cls = containing_cls

    def trav(self):
        self.type = Type(self.containing_cls.superclass, 'user')

    def __repr__(self):
        return "Super"

class ClassReferenceExpr(Expr):
    def __init__(self, cref, lines):
        self.lines = lines
        self.classref = cref

    def trav(self):
        self.type = Type(self.classref.name, 'class-literal')

    def __repr__(self):
        return "ClassReference({0})".format(self.classref.name)

class ArrayAccessExpr(Expr):
    def __init__(self, base, index, lines):
        self.lines = lines
        self.base = base
        self.index = index

    def trav(self):
        self.base.trav()
        self.index.trav()
        # TODO:
        if self.index.type == Type('int') and self.base.type.kind == 'array':
            self.type = self.base.type.typename
        else:
            self.type = Type('error')

    def __repr__(self):
        return "Array-access({0}, {1})".format(self.base, self.index)

class NewArrayExpr(Expr):
    def __init__(self, basetype, args, lines):
        self.lines = lines
        self.basetype = basetype # Type object
        self.args = args # from dim_expr_plus, [expr1, expr2, expr3, ...]

    def trav(self):
        self.args.trav()

        type_valid = True
        for args in self.args:
            if args.type != Type('int'):
                type_valid = False
                break

        if type_valid:
            self.type = self.basetype
        else:
            self.type = Type('error')

    def __repr__(self):
        return "New-array({0}, {1})".format(self.basetype, self.args)