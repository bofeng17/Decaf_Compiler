import sys

class ClassRecord:
    """Record for decaf classes"""
    def __init__(self, clsName, superClsName, ctors, methods, fields):
        self.__clsName = clsName # str
        self.__superClsName = superClsName # maybe empty str
        self.__ctors = ctors
        self.__methods = methods
        self.__fields = fields

    def getClsName(self): return self.__clsName

    def Print(self):
        print 'Class Name: ' + self.__clsName
        print 'Super Class Name: ' + self.__superClsName
        print 'Fields: '
        for item in self.__fields:
            item.Print()
        print 'Construtors: '
        for item in self.__ctors:
            item.Print()
        print 'Methods: '
        for item in self.__methods:
            item.Print()
        print '--------------------------------------------------------------------------------'

#var rec tables's var Id is assigned in TOP-DOWN manner
class CtorRecord:
    """Record for decaf Constructors"""
    def __init__(self, ctorVis, ctorParams, varTab, ctorBody):
        self.__ctorId = CtorTable.assignId()
        self.__ctorParams = ctorParams # list of formal IDs in varTab
        self.__varTab = varTab#VariableTable after flatten, but with scope info
        self.__ctorBody = ctorBody
        self.__Vis = ctorVis

    def Print(self):
        print 'CONSTRUCTOR: ' + str(self.__ctorId) + ',' + self.__Vis
        print 'Constructor parameters:'
        for id in self.__ctorParams:
            print str(id) + ', ',
        print 'Variable Table: '
        for varRec in self.__varTab.getVarTable():
            varRec.Print()
        print 'Constructor Body: '
        self.__ctorBody.Print()


#var rec tables's var Id is assigned in TOP-DOWN manner
class MethodRecord:
    """Record for decaf methods"""
    def __init__(self, methName, methParams, containingCls, methVis, methApp, retType, varTab, methBody):
        self.__methName = methName
        self.__methId = MethodTable.assignId()
        self.__methParams = methParams
        self.__containingCls = containingCls
        self.__methVis = methVis
        self.__methApp = methApp
        self.__retType = retType # TODO: currently str, instead of type record
        self.__varTab = varTab #VariableTable after flatten, but with scope info
        self.__methBody = methBody

    def Print(self):
        print 'METHOD: '+str(self.__methId)+', '+self.__methName+', '+self.__containingCls+', '+self.__methVis+', '+self.__methApp+', '+self.__retType
        print 'Method parameters:',
        start = 0
        end = len(self.__methParams)
        for id in self.__methParams:
            print str(id.getVarId()),
            if(start < end -1):
                print ",",
        print ''
        print 'Variable Table: '
        for varRec in self.__varTab.getVarTable():
            varRec.Print()
        print 'Method Body: '
        self.__methBody.Print()


class ClassTable:
    """The table to store all class intances created"""
    ClassRecords = []

    @staticmethod
    def findRecordByName(clsName): # search id in a scope descendent manner, return the closest match
        for rec in ClassTable.ClassRecords:
            if rec.getClsName() == clsName:
                return rec
        return None

    @staticmethod
    def Print():
        print '--------------------------------------------------------------------------------'
        for classRec in ClassTable.ClassRecords:
            classRec.Print()


#TODO: we probably dont need a global ctor table
class CtorTable:
    """The table to store all Ctor intances created"""
    CurCtorId = 0
    CtorRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        CtorTable.CurCtorId += 1
        return CtorTable.CurCtorId

#TODO: we probably dont need a global method table
class MethodTable:
    """The table to store all method intances created"""
    CurMethodId = 0
    MethodRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        MethodTable.CurMethodId += 1
        return MethodTable.CurMethodId
    @staticmethod
    def addMethodToGlobMethodTab(methodrec):
        MethodTable.MethodRecords.append(methodrec)

#TODO: we probably dont need a global field table
class FieldTable:
    """The table to store all method intances created"""
    CurFieldId = 0
    FieldRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        FieldTable.CurFieldId += 1
        return FieldTable.CurFieldId

    @staticmethod
    def findFieldByName(Name, curClass):
        for fr in FieldTable.FieldRecords:
            if (fr.getFieldName() == Name) and (fr.getContainingCls() == curClass):
                return True
        return False

#resemble the initialization of FieldRecord,
#the contructor takes var_cls as input
class VariableRecord:
    """Record for decaf variables
       varKind: formal/local
    """
    #var is type: var_cls
    def __init__(self, var, varKind, scope):
        self.__varName = var.getVarName()
        self.__varId = None
        self.__varKind = varKind # str: formal or local
        self.__varType = var.getType()# var_cls will construct a type_record
        self.__scope = scope
    def SetKind(self, kind):
        self.__varKind = kind

    def SetVarType(self, varType):
        self.__varType = varType

    def getVarType(self):
        return self.__varType

    def getVarKind(self):
        return self.__varKind

    def getVarId(self):
        return self.__varId

    def setVarId(self, varId):
        self.__varId = varId;

    def getScope(self):
        return self.__scope

    def getVarName(self):
        return self.__varName

    def Print(self):
        print 'VARIABLE ' + str(self.__varId) + ', ' + self.__varName + ', ' + self.__varKind + ', ',
        self.__varType.Print()
        print ''


#There will be two kind of varRec tables during AST construction
#One is formal parameters
#Two is local variables
#When merge them, merge the local var table into formal var table
#Variabletable should contain a list of variablerecords defined above

#also each variabletable and its element var_records should have a scope
class VariableTable:
    """A table of variables for a ctor/method"""
    def __init__(self):
        self.__varTable = []
        self.__recCnt = 0

    def isTableEmpty(self):
        return len(self.__VarTable) == 0

    def addVarRecord(self, varRecord, linenoRange, curScope):
        if self.findRecByNameInSameScope(varRecord.getVarName(), curScope):
            print 'VariableNameDuplication Error for Variable "' + varRecord.getVarName() + '" at lineno ',
            PrintLineNo(linenoRange[0])
            sys.exit(-1)
        self.__varTable.append(varRecord)
        self.__recCnt += 1
        varRecord.setVarId(self.__recCnt)

    def getVarTable(self): return self.__varTable

    def mergeVariableTable(self, var_table):
        for var_rec in var_table.getVarTable():
            self.addVarRecord(var_rec)

    def getAllFormalsOrLocals(self, kind):
        ret = []
        for var in self.__varTable:
            if var.getVarKind() == kind:
                 ret.append(var)
        return ret # list of all formal or local var_records

    def findRecordByName(self, Name, curScope): # search id in a scope descendent manner, return the closest match
        i = curScope
        while i >= 0:
            for rec in self.__varTable:
                if rec.getVarName() == Name and rec.getScope() == i:
                    return rec
            i -= 1
        return None

    def findRecByNameInSameScope(self, Name, curScope):
        for rec in self.__varTable:
            if rec.getVarName() == Name and rec.getScope() == curScope:
                return rec
        return None


#Note: TypeRecord is the type of VariableRecord's __varType field
class TypeRecord:
    """Record for decaf type"""
    def __init__(self, basetype, arraydim):
        self.__baseType = basetype
        self.__arrayDim = arraydim #arrayDim is a list of ['array', ...]

    def Print(self):
        for dim in self.__arrayDim:
            print dim + '(',
        print self.__baseType,
        print ')'*len(self.__arrayDim),

class var_cls:
    def __init__(self, varName, arrayDim, varType):
        self.__varName = varName
        self.__arrayDim = arrayDim # list, empyt initially
        self.__varBaseType = varType#This is the base type
        self.__Loc_or_formal = None
    def addArrayDim(self): self.__arrayDim.append('array')
    def setType(self, varType):
        self.__varBaseType = varType
    def getType(self):
        assert self.__varBaseType != None#for debug
        type_record = TypeRecord(self.__varBaseType, self.__arrayDim)
        return type_record
    def getVarName(self): return self.__varName
    def setLocOrFormal(self, loc_formal):
        self.__Loc_or_formal = loc_formal

class var_cls_list:
    def __init__(self):
        self.__var_list = []
    def addVar(self, var):
        self.__var_list.append(var)
    def setType(self, varType):
        for var in self.__var_list:
            var.setType(varType)
    def setLocOrFormal(self, loc_formal):
        for var in self.__var_list:
            var.setLocOrFormal(loc_formal)
    def getVarList(self):
        return self.__var_list

class field_cls_list:
    def __init__(self):
        self.__field_list = []
    def addField(self, field):
        self.__field_list.append(field)
    def mergeList(self, field_list):
        self.__field_list = self.__field_list + field_list.getFieldList() # TODO: correctness
    def getFieldList(self):
        return self.__field_list

class mod_cls:
    def __init__(self, vis, app):
        self.__Vis = vis
        self.__App = app
    def getVis(self):return self.__Vis
    def getApp(self):return self.__App

class FieldRecord:
    """Record for decaf fields"""
    def __init__(self, mod, var, containingCls): #var is of type: var_cls
        self.__fieldName = var.getVarName()
        self.__fieldId = FieldTable.assignId()
        self.__containingCls = containingCls
        self.__fieldVis = mod.getVis() # public or private, default is private
        self.__fieldApp = mod.getApp() # static or instance
        self.__fieldType = var.getType()# __fieldtype will get a TypeRecord


    def getFieldId(self): return self.__fieldId
    def getFieldName(self): return self.__fieldName
    def getContainingCls(self): return self.__containingCls

    def Print(self):
        # All in same line
        print 'FIELD:',
        print self.__fieldId, ',', self.__fieldName, ',',
        print self.__containingCls, ',', self.__fieldVis, ',',
        print self.__fieldApp, ',',
        self.__fieldType.Print()
        print ''

#need to add a flag to indicate this is a field_rec_list, a method or a ctor
class cls_body_decl:
    def __init__(self):
        self.__field_list = []
        self.__method = None
        self.__ctor = None
        self.__flag = ""
    def addFieldList(self, field_rec_list):
        self.__field_list = self.__field_list + field_rec_list.getFieldList()
        self.__flag = "field_list"
    def addMethod(self, meth_rec):
        self.__method = meth_rec
        self.__flag = "method"
    def addCtor(self, ctor_rec):
        self.__ctor = ctor_rec
        self.__flag = "ctor"

    def getFieldList(self):return self.__field_list
    def getMethod(self):return self.__method
    def getCtor(self):return self.__ctor
    def getFlag(self):return self.__flag

#contain 3 lists:
#   ctor list
#   method list
#   field list
## NOTE: each list contains directly field_list, method_record and ctor_record  defined above
class cls_body_decl_list:
    def __init__(self):
        self.__field_list = []
        self.__method_list = []
        self.__ctor_list = []

    def addBodyDecl(self, body_decl, linenoRange): # linenorange only for filedNameDuplication Check
        if body_decl.getFlag() == "field_list":
            self.addFieldList(body_decl, linenoRange)
        elif body_decl.getFlag() == "method":
            self.addMethod(body_decl)
        elif body_decl.getFlag() == "ctor":
            self.addCtor(body_decl)
    def addFieldList(self, body_decl, linenoRange):
        for field in body_decl.getFieldList():
            if self.findFieldByName(field.getFieldName()):
                print 'FieldNameDuplication Error for Field "' + field.getFieldName() + '" at lineno ',
                PrintLineNo(linenoRange[0])
                sys.exit(-1)
        self.__field_list.append(field)
    def addMethod(self, body_decl):
        self.__method_list.append(body_decl.getMethod())
    def addCtor(self, body_decl):
        self.__ctor_list.append(body_decl.getCtor())
    def getFieldList(self):return self.__field_list
    def getMethodList(self):return self.__method_list
    def getCtorList(self):return self.__ctor_list#TODO: probably not allow more than one ctor

    def findFieldByName(self, fieldName): # detect whether there is a field with the same name
        if self.__field_list is not None: 
            for field in self.__field_list:
                if field.getFieldName() == fieldName:
                    return True
        return False



"""Below are statements related classes ############################################"""
class Stmt(object):
    def __init__(self, linenoRange): # linenoRange: (startlineno, endlineno)
        self.__linenoRange = linenoRange

    def getScope(self, scope):return self.__scope

    def setLinenoRange(self, range):self.__linenoRange = range
    def getLinenoRange(self):return self.__linenoRange

#each block stmt should have a scope, and all stmts in this block stmt has the same scope
class BlockStmt(Stmt):
    def __init__(self, linenoRange):
        self.__StmtList = [] # Stmt object list
        super(BlockStmt, self).__init__(linenoRange)

    def addStmt(self, item):
        self.__StmtList.append(item)

    def Print(self):
        print 'Block([' # with '\n'
        for stmt in self.__StmtList:
            stmt.Print()
        print '])'

class IfStmt(Stmt):
    def __init__(self, linenoRange, condExpr, thenStmt, elseStmt = None):
        self.__condExpr = condExpr # Expr
        self.__thenStmt = thenStmt # Stmt
        self.__elseStmt = elseStmt # Stmt, may be SkipStmt
        super(IfStmt, self).__init__(linenoRange)

    def Print(self):
        print 'If(',
        self.__condExpr.Print()
        print ', ' # with '\n'
        self.__thenStmt.Print()
        print ', ' # with '\n'
        self.__elseStmt.Print()
        print ')'

class WhileStmt(Stmt):
    def __init__(self, linenoRange, condExpr, bodyStmt):
        self.__condExpr = condExpr # Expr
        self.__bodyStmt = bodyStmt # Stmt
        super(WhileStmt, self).__init__(linenoRange)

    def Print(self):
        print 'While(',
        self.__condExpr.Print()
        print ', ' # with '\n'
        self.__bodyStmt.Print() # TODO: should bodyStmt be printed in same line?
        print ')'

class ForStmt(Stmt):
    def __init__(self, linenoRange, initExpr, lpCondExpr, updExpr, bodyStmt):
        self.__initExpr = initExpr # StmtExpr, may be EmptyExpr
        self.__lpCondExpr = lpCondExpr # Expr, may be EmptyExpr
        self.__updExpr = updExpr # StmtExpr, may be EmptyExpr
        self.__bodyStmt = bodyStmt # Stmt
        super(ForStmt, self).__init__(linenoRange)

    def Print(self):
        print 'For(',
        self.__initExpr.Print()
        print ', ',
        self.__lpCondExpr.Print()
        print ', ',
        self.__updExpr.Print()
        print ', ' # with '\n'
        self.__bodyStmt.Print() # TODO: should bodyStmt be printed in same line?
        print ')'

class RetStmt(Stmt):
    def __init__(self, linenoRange, retValExpr):
        self.__retValExpr = retValExpr # Expr, may be EmptyExpr
        super(RetStmt, self).__init__(linenoRange)

    def Print(self):
        print 'Return(',
        self.__retValExpr.Print()
        print ')'

class ContStmt(Stmt):
    def __init__(self, linenoRange):
        super(ContStmt, self).__init__(linenoRange)

    def Print(self):
        print 'Continue()'

class BrkStmt(Stmt):
    def __init__(self, linenoRange):
        super(BrkStmt, self).__init__(linenoRange)

    def Print(self):
        print 'Break()'

class SkipStmt(Stmt):
    def __init__(self, linenoRange): # don't care linenoRange
        super(SkipStmt, self).__init__(linenoRange)

    def Print(self):
        print 'Skip()'

class StmtExprStmt(Stmt):
    def __init__(self, linenoRange, StmtExpr):
        self.__StmtExpr = StmtExpr # AssnExpr/AutoExpr/MethodInvExpr
        super(StmtExprStmt, self).__init__(linenoRange)

    def Print(self):
        print 'Expr(',
        self.__StmtExpr.Print()
        print ')'

class VarDeclStmt(Stmt): # TODO: do we really need this kind of statement?
    def __init__(self, linenoRange):
        super(VarDeclStmt, self).__init__(linenoRange)

    def Print(self):
        pass # print nothing



"""Below are expression related classes ############################################"""
class Expr(object):
    def __init__(self, linenoRange): # linenoRange: (startlineno, endlineno)
        self.__linenoRange = linenoRange
    def setLinenoRange(self, linenoRange):
        self.__linenoRange = linenoRange
    def getLinenoRange(self):
        return self.__linenoRange
    def Print(self):
        assert False,"should never be called"

class ConstExpr(Expr):
    def __init__(self, linenoRange, expr_type, val):
        self.__type = expr_type # str: 'Integer-constant', 'Float-constant', 'String-constant', 'Null', 'True', 'False'
        self.__val = val # int: 'Integer-constant', float: 'Float-constant', str: 'String-constant', None for others
        super(ConstExpr, self).__init__(linenoRange)
    def Print(self):
        print "Constant(",
        if self.__type == "Integer-constant":
            print "Integer-constant(",
        if self.__type == "Float-constant":
            print "Float-constant(",
        if self.__type == "String-constant":
            print "String-constant(",
        print self.__val,
        print ")",
        print ")",

class VarExpr(Expr):
    def __init__(self, varRec,linenoRange):
        self.__variableRecord = varRec
        super(VarExpr, self).__init__(linenoRange)
    def Print(self):
        print "Variable(",
        print self.__variableRecord.getVarId(),
        print ")",

class UnaryExpr(Expr):
    def __init__(self, linenoRange, operand, unaryOperator):
        self.__operand = operand; # Expr
        self.__unaryOperator = unaryOperator; # str
        super(UnaryExpr, self).__init__(linenoRange)
    def Print(self):
        print "Unary(",
        print self.__unaryOperator+",",
        self.__operand.Print()
        print ")",

class BinaryExpr(Expr):
    def __init__(self, linenoRange, operand1, operator, operand2):
        self.__operand1 = operand1; # Expr
        self.__operator = operator; # str
        self.__operand2 = operand2; # Expr
        super(BinaryExpr, self).__init__(linenoRange)
    def Print(self):
        print "Binary(",
        print self.__operator+", ",
        self.__operand1.Print()
        print ",",
        self.__operand2.Print()
        print ")",

class AssnExpr(Expr):
    def __init__(self, linenoRange, lhs, rhs):
        self.__lhs = lhs # FieldAccExpr/ArryAccExpr
        self.__rhs = rhs # Expr
        super(AssnExpr, self).__init__(linenoRange)
    def Print(self):
        print "Assign(",
        self.__lhs.Print()
        print ",",
        self.__rhs.Print()
        print ")",

class AutoExpr(Expr):
    def __init__(self, linenoRange, lhs, operator, loc):
        self.__lhs = lhs # FieldAccExpr/ArryAccExpr
        self.__operator = operator # str: 'inc' or 'dec'
        self.__loc = loc # str: 'post' or 'pre'
        super(AutoExpr, self).__init__(linenoRange)
    def Print(self):
        print "Auto(",
        self.__lhs.Print()
        print ",",
        print self.__operator+",",
        print self.__loc,
        print ")",

class FieldAccExpr(Expr):
    def __init__(self, linenoRange, baseClsExpr, accessId):
        self.__baseClsExpr = baseClsExpr # maybe ExmptyExpr
        self.__accessId = accessId
        super(FieldAccExpr, self).__init__(linenoRange)
    def getBaseClsExpr(self):return self.__baseClsExpr
    def getAccessId(self):return self.__accessId

    def Print(self):
        print "Field-access(",
        self.__baseClsExpr.Print()
        print ",",
        print self.__accessId,
        print ")",

class MethodInvExpr(Expr):
    def __init__(self, linenoRange, baseClsExpr, methNameStr, args):
        self.__baseClsExpr = baseClsExpr
        self.__methNameStr = methNameStr
        self.__args = args#type: args_plus_cls
        super(MethodInvExpr, self).__init__(linenoRange)
    def Print(self):
        print "Method-call(",

        self.__baseClsExpr.Print()
        print ",",

        print self.__methNameStr+",",
        print '[',
        printCommaSepaExprs(self.__args.getArgsList())
        print ']',
        print ")",

def printCommaSepaExprs(expr_list):
    start = 0
    end = len(expr_list)
    for expr in expr_list:
        expr.Print()
        if start < end - 1:
            print ",",
        start+=1

class NewObjExpr(Expr):
    def __init__(self, linenoRange, baseClsName, args):
        self.__baseClsName = baseClsName#should be just string
        self.__args = args#type: args_plus_cls
        super(NewObjExpr, self).__init__(linenoRange)
    def Print(self):
        print "New-object(",
        print self.__baseClsName+",",
        print '[',
        printCommaSepaExprs(self.__args.getArgsList())
        print ']',
        print ")",

class ThisExpr(Expr):
    def __init__(self, linenoRange):
        super(ThisExpr, self).__init__(linenoRange)
    def Print(self):
        print 'This',

class SuperExpr(Expr):
    def __init__(self, linenoRange):
        super(SuperExpr, self).__init__(linenoRange)
    def Print(self):
        print 'Super',

class ClsRefExpr(Expr):
    def __init__(self, linenoRange, className):
        self.__className = className
        super(ClsRefExpr, self).__init__(linenoRange)
    def Print(self):
        print "Class-reference(",
        print self.__className,
        print ")",

class ArryAccExpr(Expr):
    def __init__(self, linenoRange, base_expr, index_expr):
        self.__baseExpr = base_expr
        self.__indexExpr = index_expr
        super(ArryAccExpr, self).__init__(linenoRange)
    def Print(self):
        print "ArrayAccess(",
        self.__baseExpr.Print()
        print ', ',
        self.__indexExpr.Print()
        print ")",

class NewArryExpr(Expr):
    def __init__(self, linenoRange, base, dimexpr):#base is a str,
        self.__base = base#[array, array, ..., baseTYpe]
        self.__dimexpr = dimexpr # [dim1, dim2, ...]
        super(NewArryExpr, self).__init__(linenoRange)
    def Print(self):
        print "New-arrayr(", #print 'New-array( '

        for each in self.__base:#print 'array(array(...array(baseType))), '
            if each == 'array':
                print each + '(',
            else:
                print each,
        for each in self.__base:
            if each == 'array':
                print ')',
        print ", ",
        printCommaSepaExprs(self.__dimexpr)
        print ')',

class EmptyExpr(Expr):
    def __init__(self, linenoRange):
        super(EmptyExpr, self).__init__(linenoRange)

    def Print(self):
        print "Empty",



class args_plus_cls(): # Expr, Expr , ..., Expr
    def __init__(self):
        self.__args_list = []
    def addArgs(self, arg): # arg: Expr
        self.__args_list.append(arg)
    def getArgsList(self):
        return self.__args_list

def PrintLineNo(lineno):
    print lineno - 12

# class ClassNameDuplicationException(Exception):
#     def __init__ (self, clsName):
#         self.__clsName = clsName
#         print self.__clsName

# class FieldNameDuplicationException(Exception):
#     def __init__ (self, fieldName):
#         self.__fieldName = fieldName

# class VariableNameDuplicationException(Exception):
#     def __init__ (self, varName):
#         self.__varName = varName


