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
        for var in __varTable:
            if var.getVarType() == 'formal':
                 formals.append(var.getVarId())
        return formals # list of all formal IDs



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

class FieldRecord:
    """Record for decaf fields"""
    def __init__(self, fieldName, containingCls, fieldVis, fieldApp, fieldType):
        self.__fieldName = fieldName
        self.__fieldId = FieldTable.assignId()
        self.__containingCls = containingCls
        self.__fieldVis = fieldVis # public or private, default is private
        self.__fieldApp = fieldApp # static or instance
        self.__fieldType = fieldType

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










"""             imtermediate classes                  """

