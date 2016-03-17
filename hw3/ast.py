from operator import add
class TypeRecord:
    """Record for decaf type"""
    def __init__(self):
        self.__typeList = [] # e.g. [array, array, int]

    def append(self, item):
        self.__typeList.append(item)





class VariableRecord:
    """Record for decaf variables
       varKind: formal/local
    """
    def __init__(self, varName, varId, varKind, varType):
        self.__varName = varName
        self.__varId = varId
        self.__varKind = varKind # str: formal or local
        self.__varType = varType
    def SetKind(self, kind):
        self.__varKind = kind
    def SetType(self, varType):
        self.__varType = varType

    def getVarType(self):
        return self.__varType
    def getVarId(self):
        return self.__varId

    def setVarId(self, varId):
        self.__varId = varId;




class ClassRecord:
    """Record for decaf classes"""
    def __init__(self, clsName, superClsName, ctors, methods, fields):
        self.__clsName = clsName
        self.__superClsName = superClsName
        self.__ctors = ctors
        self.__methods = methods
        self.__fields = fields


class CtorRecord:
    """Record for decaf Constructors"""
    def __init__(self, ctorVis, ctorParams, varTab, ctorBody):
        self.__ctorId = CtorTable.assignId()
        self.__ctorParams = ctorParams # list of formal IDs in varTab
        self.__varTab = varTab
        self.__ctorBody = ctorBody
        self.__Vis = ctorVis

class MethodRecord:
    """Record for decaf methods"""
    def __init__(self, methName, containingCls, methVis, methApp, retType, varTab, methBody):
        self.__methName = methName
        self.__methId = MethodTable.assignId()
        self.__containingCls = containingCls
        self.__methVis = methVis
        self.__methApp = methApp
        self.__retType = retType
        self.__varTab = varTab
        self.__methBody = methBody

    def setContainingCls(self, clsName):
        self.__containingCls = clsName





class ClassTable:
    """The table to store all class intances created"""
    ClassRecords = []

class CtorTable:
    """The table to store all Ctor intances created"""
    CurCtorId = 0
    CtorRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        CtorTable.CurCtorId += 1
        return CtorTable.CurCtorId;

class MethodTable:
    """The table to store all method intances created"""
    CurMethodId = 0
    MethodRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        MethodTable.CurMethodId += 1
        return MethodTable.CurMethodId;

class FieldTable:
    """The table to store all method intances created"""
    CurFieldId = 0
    FieldRecords = []

    @staticmethod
    def assignId(): # Id starts from 1
        FieldTable.CurFieldId += 1
        return FieldTable.CurFieldId;
    @staticmethod
    def addFieldToGlobFieldTab(field):
        FieldTable.FieldRecords.append(field)






class VariableTable:
    """A table of variables for a ctor/method"""
    def __init__(self):
        self.__varTable = []
        self.__curVarId = 0

    def assignId(self): # Id starts from 1
        self.__curVarId += 1
        return self.__curVarId;
    def AddVar(self, varRecord):
        self.__varTable.append(varRecord)

    def mergeRecordList(self, recList):
        for rec in recList:
            rec.setVarId(self.assignId())
            self.AddVar(rec)

    def getAllFormals(self):
        formals = []
        for var in self.__varTable:
            if var.getVarType() == 'formal':
                 formals.append(var.getVarId())
        return formals # list of all formal IDs




class var_cls:
    def __init__(self, varId, arrayDim, varType, lineno):
        self.__varId = varId
        self.__arrayDim = arrayDim
        self.__lineno = lineno
        self.__varType = varType
    def addArrayDim(self):
        self.__arrayDim.append('array')
    def setType(self, varType):
        self.__varType = varType
    def getVarId(self):
        return self.__varId
    def getType(self):
        return self.__varType

class var_cls_list:
    def __init__(self):
        self.__var_list = []
    def addVar(self, var):
        self.__var_list.append(var)
    def setType(self, varType):
        for var in self.__var_list:
            var.setType(varType)
class field_cls_list:
    def __init__(self):
        self.__field_list = []
    def addField(self, field):
        self.__field_list.append(field)
    def mergeList(self, field_list):
        self.__field_list = map(add, self.__field_list, field_list)

class mod_cls:
    def __init__(self, vis, app):
        self.__Vis = vis
        self.__App = app
    def getVis(self):return self.__Vis
    def getApp(self):return self.__App

class FieldRecord:
    """Record for decaf fields"""
    def __init__(self, mod, var):
        self.__fieldName = var.getVarId()
        self.__fieldId = FieldTable.assignId()
        self.__containingCls = ""
        self.__fieldVis = mod.getVis() # public or private, default is private
        self.__fieldApp = mod.getApp() # static or instance
        self.__fieldType = var.getType()

    def setContainingCls(self, clsName):
        self.__containingCls = clsName

#need to add a flag to indicate this is a field_rec_list, a method or a ctor
class cls_body_decl:
    def __init__(self):
        self.__field_list = []
        self.__method = None
        self.__ctor = None
        self.__flag = ""
    def addFieldList(self, field_rec_list):
        self.__field_list = map(add, self.__field_list, field_rec_list)
        self.__flag = "field_list"
    def addMethod(self, meth_rec):
        self.__method = meth_rec
        self.__flag = "method"
    def addCtor(self, ctor_rec):
        self.__ctor = ctor_rec
        self.flag = "ctor"

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
    def addBodyDecl(self, body_decl):
        if body_decl.getFlag() == "field_list":
            self.addFieldList(body_decl)
        elif body_decl.getFlag() == "method":
            self.addMethod(body_decl)
        elif body_decl.getFlag() == "ctor":
            self.addCtor(body_decl)
    def addFieldList(self, body_decl):
        self.__field_list = map(add, self.__field_list, body_decl.getFieldList())
    def addMethod(self, body_decl):
        self.__method_list.append(body_decl.getMethod())
    def addCtor(self, body_decl):
        self.__ctor_list.append(body_decl.getCtor())
    def setContainingCls(self, clsName):
        for field in self.__field_list:
            field.setContainingCls(clsName)
        for method in self.__method_list:
            method.setContainingCls(clsName)
        for ctor in self.__ctor_list:
            ctor.setContainingCls(clsName)
    def getFieldList(self):return self.__field_list
    def getMethodList(self):return self.__method_list
    def getCtorList(self):return self.__ctor_list#TODO: probably not allow more than one ctor


class Stmt:
    def __init__(self, linenoRange): # linenoRange: (startlineno, endlineno)
        self.linenoRange = linenoRange
    
    def setLinenoRange(self, range):
        self.linenoRange = range

class IfStmt(Stmt):
    def __init__(self, linenoRange, condExpr, thenStmt, elseStmt = None):
        self.__condExpr = condExpr # Expr
        self.__thenStmt = thenStmt # Stmt
        self.__elseStmt = elseStmt # Stmt, may be None
        Stmt.__init__(self, linenoRange)

class WhileStmt(Stmt):
    def __init__(self, linenoRange, conExpr, bodyStmt):
        self.__condExpr = condExpr # Expr
        self.__bodyStmt = bodyStmt # Stmt
        Stmt.__init__(self, linenoRange)

class ForStmt(Stmt):
    def __init__(self, linenoRange, initExpr, lpCondExpr, updExpr, bodyStmt):
        self.__initExpr = initExpr # StmtExpr, may be None
        self.__lpCondExpr = lpCondExpr # Expr, may be None
        self.__updExpr = updExpr # StmtExpr, may be None
        self.__bodyStmt = bodyStmt # Stmt
        Stmt.__init__(self, linenoRange)

class RetStmt(Stmt):
    def __init__(self, linenoRange, retValExpr = None):
        self.__retValExpr = retValExpr # Expr, may be None
        Stmt.__init__(self, linenoRange)

class BlockStmt(Stmt):
    def __init__(self, linenoRange):
        self.__StmtList = [] # Stmt object list
        Stmt.__init__(self, linenoRange)

    def append(self, item):
        self.__StmtList.append(item)

class ContStmt(Stmt):
    def __init__(self, linenoRange):
        Stmt.__init__(self, linenoRange)

class BrkStmt(Stmt):
    def __init__(self, linenoRange):
        Stmt.__init__(self, linenoRange)

class SkipStmt(Stmt):
    def __init__(self, linenoRange):
        Stmt.__init__(self, linenoRange)

class StmtExprStmt(Stmt):
    def __init__(self, linenoRange, StmtExpr):
        # TODO: May need one more layer of abstration-StmtExpr Class.
        self.__StmtExpr = StmtExpr # AssnExpr/AutoExpr/MethodInvExpr
        Stmt.__init__(self, linenoRange)

# TODO:
class VarDeclStmt(Stmt):
    def __init__(self, linenoRange):
        Stmt.__init__(self, linenoRange)

# TODO: all things below
class Expr:
    def __init__(self, linenoRange): # linenoRange: (startlineno, endlineno)
        self.__linenoRange = linenoRange

class ConstExpr(Expr):
    def __init__(self, linenoRange, type, val):
        self.__type = type # str: 'Integer-constant'
        self.__val = val # int: 'Integer-constant', 
        Expr.__init__(self, linenoRange)

class VarExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class UnaryExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class BinaryExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class AssnExpr(Expr):
    def __init__(self, linenoRange, lhs, rhs):
        # TODO: May need one more layer of abstration.
        self.__lhs = lhs # FieldAccExpr/ArryAccExpr
        self.__rhs = rhs # Expr
        Expr.__init__(self, linenoRange)

class AutoExpr(Expr):
    def __init__(self, linenoRange, lhs, operator, loc):
        # TODO: May need one more layer of abstration.
        self.__lhs = lhs # FieldAccExpr/ArryAccExpr
        self.__operator = operator # str: 'inc' or 'dec'
        self.__loc = loc # str: 'post' or 'pre'
        Expr.__init__(self, linenoRange)

class FieldAccExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class MethodInvExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class NewObjExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class ThisExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class SuperExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class ClsRefExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class ArryAccExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)

class NewArryExpr(Expr):
    def __init__(self, linenoRange):
        
        Expr.__init__(self, linenoRange)









