challenge 1: how to  find the current variable table and the scope of current parsing statement
>>solution: use a global variable denote the current variabletbale, and the curscope global variable mentioned next will be used to indicate the scope of current stmt
curVarTable = None # variable talbe of current block. Set by param_list (formals), accessed by var_decl(locals)
    
challenge 2: how to know scope when adding variable records to variable table
>>solutions: use a global variable and added two productions,
curScope = -1 # global var
# handle scope inc/dec
def p_scope_inc(p):
    'scope_inc : '
    global curScope
    curScope += 1
def p_scope_dec(p):
    'scope_dec : '
    global curScope
    curScope -= 1
the moment we see '{', the curscope += 1
the moment we see '}', the curscope -= 1


challenge 3: when resolving field, ctor, method, etc, we didn't wait until all stmts get resolved, instead we set class at the time when we are about to shift a stmt/field/method
>>Solution:
    use global variable: curClass
    curClass = None # set by class_decl, accessed by field_decl, field_access
    so during the reduction of the sub components, we know what class we are currently parsing






types:
    format: [array, array, *, basetype]
    we check the basetype, if it's one of the built-in type, then we treat it as built-in types otherwise it's user defined type
class TypeRecord:
    """Record for decaf type"""
    def __init__(self, basetype, arraydim):
        self.__baseType = basetype
        self.__arrayDim = arraydim #arrayDim is a list of ['array', ...]




