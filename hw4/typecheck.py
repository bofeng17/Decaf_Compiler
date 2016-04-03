import ast
import itertools
import sys

#assuming c1 and c2 are of class Class defined in ast
def is_subclass(c1, c2, includeFlag):
    if(includeFlag == 'inclusive'):
        if(c1 is c2):
            return True
    lastcls = c1.superclass
    while(lastcls!=None):
        if(lastcls is c2):
            return True
        lastcls = lastcls.superclass
    return False

#assuming t1 and t2 are of class Type defined in ast
#check if t1 is subtype of t2, return True or False
def is_subtype(t1, t2, strict=False):

    if(not strict):
        if(t1 is t2):#Neccessary? can make it faster
            return True

        #rule No.1, t1 is same as t2
        if(t1.kind == t2.kind):
            if(t1.kind != 'array'):
                if(t1.typename == t2.typename):
                    return True
            else:
                if(t1.basetype == t2.basetype):
                    return True

    #rule No.2:int is subtype of float
    if(t1.kind == 'basic' and t2.kind == 'basic'):
        if(t1.typename == 'int' and t2.typename == 'float'):
            return True

    #rule No.3 and No.7
    if(t1.kind == 'user' and t2.kind == 'user' \
       or t1.kind == 'class-literal' and t2.kind == 'class-literal'):
        t1_cls = ast.lookup(ast.classtable,t1.typename)
        t2_cls = ast.lookup(ast.classtable,t2.typename)
        if(t1_cls!=None and t2_cls!=None):
            if is_subclass(t1_cls, t2_cls, 'inclusive'):
                return True
    #if t1 is null, and t2 is user or array, unless t2_class does not exist, return true
    #rule No.4 and No.6
    if(t1.kind == 'basic' and t2.kind in ['user','array']):
        if(t1.typename == 'null'):
            t2_cls = ast.lookup(ast.classtable,t2.typename)
            if(t2_cls is None):
                return False
            return True

    #rule No.5
    if(t1.kind == 'array' and t2.kind == 'array'):
        return is_subtype(t1.basetype, t2.basetype)
#anything else just return False
    return False



def is_subtype_args(args1, args2, strict=False):
    if(len(args1) == len(args2)):
        subtype_ok = True
        for a1, a2 in itertools.izip(args1, args2):
            if(not is_subtype(a1, a2, strict)):
                subtype_ok = False
                break
        return subtype_ok
    return False

def try_add(m_set, m):
    if(len(m_set) == 0):
        m_set.add(m)
    else:
        add_new_cand = True
        elem_to_remove = []
        for old_m in m_set:
            arg_types = m.vars.get_params_types()
            old_arg_types = old_m.vars.get_params_types()
            #if new cand is more concret than old cand, kick out old cand
            if(is_subtype_args(arg_types, old_arg_types)):
                elem_to_remove.append(old_m)
            #if new cand is less concret than old cand, not gonna add new cand
            #but we keep testing cuz we want to filter out as many m as we can
            elif(is_subtype_args(old_arg_types, arg_types)):
                add_new_cand = False
        if(add_new_cand):
            m_set.add(m)
        for each in elem_to_remove:
            m_set.remove(each)



def check_methods(meths):
    for check_m in meths:
        for m in meths:
            if(m.name == check_m.name and (m is not check_m)):
                check_m_types = check_m.vars.get_params_types()
                m_types = m.vars.get_params_types()
                if(not (is_subtype_args(check_m_types, m_types, True) \
                        or is_subtype_args(m_types, check_m_types, True))):
                    print "overloading methods [{0}] ID [{1}] and [{2}] have conflict arg types".format(m.name, m.id, check_m.id)
                    sys.exit(-1)



def methods_match(m1_name, m1_args, m2):
    if(m1_name == m2.name):
        m2_args = m2.vars.get_params_types()#list of types for the args
        if(is_subtype_args(m1_args, m2_args)):
            return True
    return False


def get_all_parent_cls(c):
    ret = []
    ret = ret + [c]
    p = c.superclass
    while(p is not None):
        ret = ret+[p]
        p = p.superclass
    return ret


#resolve_* functions:
#   return the field, method, ctor if success
#   otherwise return None
def resolve_field(target_cls, accessing_cls, fname, static):
    if(target_cls is None):
        return None
    cls_list = get_all_parent_cls(target_cls)
    if(cls_list is None):
        print target_cls.name,'fuck',cls_list
    for c in cls_list:
        f = ast.lookup(c.fields, fname)
        if(f != None):
            if((f.visibility == 'private') and (accessing_cls is not c)):
               continue
            if(static and f.storage == 'static'):
                return f
            if(not static and f.storage == 'instance'):
                return f
    return None

def resolve_method(target_cls, accessing_cls, mname, args, static):
    if(target_cls is None):
        return None
    cls_list = get_all_parent_cls(target_cls)
    args_type = [arg.expr_type for arg in args]
    candidate_methods=set([])
    for c in cls_list:
        for m in c.methods:
            if(methods_match(mname, args_type, m)):
                if(m.visibility == 'private' and (accessing_cls is not c)):
                    continue
                if(static and m.storage == 'static'):
                    try_add(candidate_methods, m)
                if(not static and m.storage == 'instance'):
                    try_add(candidate_methods, m)
        if(len(candidate_methods)>0):
            break
    if(len(candidate_methods) == 1):#if there is only one candidate remains
        return candidate_methods.pop()
    return None


def resolve_ctor(target_cls, accessing_cls, args):
    if(target_cls == None):
        return None
    args_type = [arg.expr_type for arg in args]
    candidate_ctors=set([])
    for ctor in target_cls.constructors:
        if(methods_match(target_cls.name, args_type, ctor)):
            if(ctor.visibility == 'private' and (accessing_cls is not target_cls)):
                continue
            try_add(candidate_ctors, ctor)
    if(len(candidate_ctors) == 1):#there is only one candidate remains
        return candidate_ctors.pop()
    return None






