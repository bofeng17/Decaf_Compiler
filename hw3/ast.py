class TypeRecord:
    """Record for decaf type"""
    def __init__(self):
        self.__typeList = []



class VariableRecord:
    """Record for decaf variables"""
    def __init__(self, varName, varId, varKind, varType):
        self.__varName = varName
        self.__varId = varId
        self.__varKind = varKind
        self.__varType = varType

class VariableTable:
    """A table of variables for a ctor/method"""
    def __init__(self):
        self.__varTable = []
    def AddVar(self, varRecord):
        self.__varTable.append(varRecord)


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
    def __init__(self, ctorId, ctorVis, ctorParams, varTab, ctorBody):
        self.__ctorId = ctorId
        self.__ctorParams = ctorParams
        self.__varTab = varTab
        self.__ctorBody = ctorBody
        self.__Vis = ctorVis

class MethodRecord:
    """Record for decaf methods"""
    def __init__(self, methName, methId, containingCls, methVis, methApp, retType, varTab, methBody):
        self.__methName = methName
        self.__methId = methId
        self.__containingCls = containingCls
        self.__methVis = methVis
        self.__methApp = methApp
        self.__retType = retType
        self.__varTab = varTab
        self.__methBody = methBody

class FieldRecord:
    """Record for decaf fields"""
    def __init__(self, fieldName, fieldId, containingCls, fieldVis, fieldApp, fieldType):
        self.__fieldName = fieldName
        self.__fieldId = fieldId
        self.__containingCls = containingCls
        self.__fieldVis = fieldVis
        self.__fieldApp = fieldApp
        self.__fieldType = fieldType




class ClassTable:
    """The table to store all class intances created"""
    ClassRecords = []

class CtorTable:
    """The table to store all Ctor intances created"""
    CurrentCtorId = 1
    CtorRecords = []

class MethodTable:
    """The table to store all method intances created"""
    CurrentMethodId = 1
    MethodRecords = []

class FieldTable:
    """The table to store all method intances created"""
    CurrentFieldId = 1
    FieldRecords = []
