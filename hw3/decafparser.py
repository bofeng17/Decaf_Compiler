#!/usr/bin/python

import ply.yacc as yacc
import decaflexer
from decaflexer import tokens
#from decaflexer import errorflag
from decaflexer import lex
import ast

import sys
import logging

precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'RPAREN'), # TODO: need to verify
    ('right', 'ELSE'),
)

curScope = -1 # global var
curVarTable = None # variable talbe of current block. Set by param_list (formals), accessed by var_decl(locals)

def init():
    decaflexer.errorflag = False

### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
    ast.ClassTable.ClassRecords.append(p[1])
def p_class_decl_list_empty(p):
    'class_decl_list : '
    pass

def p_class_decl(p):
    'class_decl : CLASS ID extends LBRACE class_body_decl_list RBRACE'
    # class_body_decl_list: [CtorRecord list, MethodRecord list, FieldRecord list]
    # classRecord: (clsName, superClsName, ctors, methods, fields)
    ast.ClassRecord(p[2], p[3], p[5].getCtorList(), p[5].getMethodList(), p[5].getFieldList())
    p[5].setContainingCls(p[2])

def p_class_decl_error(p):
    'class_decl : CLASS ID extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
    ast.ClassRecord(p[2], p[3], [], [], []) # empty CtorRecord/MethodRecord/FieldRecord list


def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0] = p[2] # p[2]: str of ID.lexeme
def p_extends_empty(p):
    ' extends : '
    p[0] = ""

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    p[1].addBodyDecl(p[2])
    p[0] = p[1]
def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0] = ast.cls_body_decl_list()
    p[0].addBodyDecl(p[1])


# class_body_decl: [CtorRecord, MethodRecord, FieldRecord partial list(because we can declare more than one Fields at one time)]
def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0] = ast.cls_body_decl()
    p[0].addFieldList(p[1])
def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0] = ast.cls_body_decl()
    p[0].addMethod(p[1])
def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0] = ast.cls_body_decl()
    p[0].addCtor(p[1])

#var_decl    type: var_cls_list
#field_decl  type: field_rec_list
#field_rec_list contains fieldrecord elem
#fieldrecord elem is init from var_cls
#fieldrecord: (fieldName, containingCls, fieldVis, fieldApp, fieldType)
#var_cls: (varId, arrayDim, varType, lineno)
#mod_cls: (Vis, App)
def p_field_decl(p):
    'field_decl : mod var_decl'
    new_field_list = ast.field_cls_list()
    for var in p[2]:
        tmp_field_rec = ast.FieldRecord(p[1] ,var)
        new_field_list.addField(tmp_field_rec)
        # ast.FieldTable.addFieldToGlobFieldTab(tmp_field_rec)
    p[0] = new_field_list

#vis: public or private
#app: static or instance

"""Scope layout:
        f(formals)
        { 0
            { 1
                { 2

                }
            }
            { 1

            }
        }

"""
def p_method_decl_void(p):
    'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
    # TODO:
    new_var_table = ast.VariableTable()
    new_var_table = p[7].getAllLocVarStmtTables(new_var_table)
    p[0] = ast.MethodRecord(p[3], None, p[1].getVis(), p[1].getApp(), "void", p[5].mergeVariableTable(new_var_table), p[7])
    p[0].assignIDsForVarTab()
    # ast.MethodTable
#vis: public or private
#app: static or instance
def p_method_decl_nonvoid(p):
    'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
    new_var_table = ast.VariableTable()
    new_var_table = p[7].getAllLocVarStmtTables(new_var_table)
    p[0] = ast.MethodRecord(p[3], None, p[1].getVis(), p[1].getApp(), p[2], p[5].mergeVariableTable(new_var_table), p[7])
    p[0].assignIDsForVarTab()

#block is type: blockStmt has a list of various kinds of stmts
#vis: public or private
#app: static or instance
def p_constructor_decl(p):
    'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
#!!!Important:construct scope first, before trying to flatten the variable tables
    p[5].setScope(0)#set formals the outterest scope

    new_var_table = ast.VariableTable()
    new_var_table = p[6].getAllLocVarStmtTables(new_var_table)
    p[0] = ast.CtorRecord(p[1].getVis(), p[4].getAllFormalsOrLocals('Formal'), p[4].mergeVariableTable(new_var_table), p[6])
    p[0].assignIDsForVarTab()


def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0] = ast.mod_cls(p[1], p[2])

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0] = p[1]
def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0] = p[1]
def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0] = "private"

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0] = p[1]
def p_storage_mod_empty(p):
    'storage_mod : '
    p[0] = "instance"

#var_decl is still of type: var_cls_list
def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    p[2].setType(p[1])
    p[0] = p[2]

def p_type_int(p):
    'type :  INT'
    p[0] = p[1]
def p_type_bool(p):
    'type :  BOOLEAN'
    p[0] = p[1]
def p_type_float(p):
    'type :  FLOAT'
    p[0] = p[1]
def p_type_id(p):
    'type :  ID'
    p[0] = p[1]

#For var_decl->field_decl->class_body_decl->class_body_decl_list
#            ->stmt
def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[1].addVar(p[3])
    p[0] = p[1]
def p_var_list_single(p):
    'var_list : var'
    new_var_list = ast.var_cls_list()
    new_var_list.addVar(p[1])
    p[0] = new_var_list

def p_var_id(p):
    'var : ID'
    # var_cls: varId, arrayDim, varType
    p[0] = ast.var_cls(p[1], [], None)

def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    p[1].addArrayDim()
    p[0] = p[1]

#param_list_opt is type: VariableTable
#TODO: for now it's blockstmt, flatten it if neccessary
def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = p[1]

def p_param_list_empty(p):
    'param_list_opt : '
    # curVarTable: global variable set by param_list (formals), accessed by var_decl(locals)
    curVarTable = ast.VariableTable()
    p[0] = curVarTable

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[1].AddVarRecord(p[3])
    p[0] = p[1]

#param_list is type: variabletable
def p_param_list_single(p):
    'param_list : param'
    # curVarTable: global variable set by param_list (formals), accessed by var_decl(locals)
    curVarTable = ast.VariableTable()
    curVarTable.AddVarRecord(p[1])
    p[0] = curVarTable

#var is type: var_cls
#param is type: variablerecord
def p_param(p):
    'param : type var'
    p[2].setType(p[1])
    p[2].setLocOrFormal('Formal')
    p[0] = ast.VariableRecord(p[2], 'formal', scope = 0)


# Statements
#block is type: blockstmt
def p_block(p):
    'block : LBRACE scope_inc stmt_list scope_dec RBRACE' # scope_inc increase var:scope by 1
    p[0] = p[2]
def p_block_error(p):
    'block : LBRACE scope_inc stmt_list error scope_dec RBRACE'
    # error within a block; skip to enclosing block
    # TODO: AST for error block
    p[0] = p[2]

#stmt_list type: BlockStmt
def p_stmt_list_empty(p):
    'stmt_list : '
    p[0] = ast.BlockStmt(p.linespan(0))
def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    p[1].addStmt(p[2])
    p[1].setLinenoRange(p.linespan(0)) # each stmt should have its own range, so shouldn't modify p[2]'s
    p[0] = p[1]


def p_stmt_if_only(p):
    'stmt : IF LPAREN expr RPAREN stmt'
    p[0] = ast.IfStmt(p.linespan(0), p[3], p[5], ast.SkipStmt(p.linespan(0)))
def p_stmt_if_else(p):
    'stmt : IF LPAREN expr RPAREN stmt ELSE stmt'
    p[0] = ast.IfStmt(p.linespan(0), p[3], p[5], p[7])
def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = ast.WhileStmt(p.linespan(0), p[3], p[5])
def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = ast.ForStmt(p.linespan(0), p[3], p[5], p[7], p[9])
def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    p[0] = ast.RetStmt(p.linespan(0), p[2])
def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = ast.StmtExprStmt(p.linespan(0), p[1])
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = ast.BrkStmt(p.linespan(0))
def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = ast.ContStmt(p.linespan(0))
def p_stmt_block(p):
    'stmt : block'
    p[0] = p[1] # p[1]: BlockStmt

#var_decl is type: var_cls_list
#we construct VariableTable out of the var_cls_list
def p_stmt_var_decl(p):
    'stmt : var_decl'
    for var in p[1]:
        varrec = ast.VariableRecord(var, 'Local', curScope)
        # curVarTable: global variable set by param_list (formals), accessed by var_decl(locals)
        curVarTable.addVarRecord(varrec)
    p[0] = ast.VarDeclStmt(p.linespan(0), curVarTable)

def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    decaflexer.errorflag = True
    p[0] = ast.SkipStmt(p.linespan(0))




# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    p[0] = ast.ConstExpr(p.linespan(0), 'Integer-constant', p[1]) # type of p[1]: int
def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0] = ast.ConstExpr(p.linespan(0), 'Float-constant', p[1]) # type of p[1]: float
def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0] = ast.ConstExpr(p.linespan(0), 'String-constant', p[1]) # type of p[1]: str
def p_literal_null(p):
    'literal : NULL'
    p[0] = ast.ConstExpr(p.linespan(0), 'Null', None)
def p_literal_true(p):
    'literal : TRUE'
    p[0] = ast.ConstExpr(p.linespan(0), 'True', None)
def p_literal_false(p):
    'literal : FALSE'
    p[0] = ast.ConstExpr(p.linespan(0), 'False', None)

#primary is just a intermiedate container, it should be one of the expr types
def p_primary_literal(p):
    'primary : literal'
    p[0] = p[1] # p[1]: constExpr
def p_primary_this(p):
    'primary : THIS'
    p[0] = ast.ThisExpr(p.linespan(0))
def p_primary_super(p):
    'primary : SUPER'
    p[0] = ast.SuperExpr(p.linespan(0))
def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    p[0] = p[1]

def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    p[0] = ast.NewObjExpr(p.linespan(0), p[2], p[4])

def p_primary_lhs(p):
    'primary : lhs'#lhs should be one of the access_exprs
    p[0] = p[1]

def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = p[1]

def p_args_opt_nonempty(p):
    'args_opt : arg_plus' #args_opt is type: args_plus_cls
    p[0] = p[1]
def p_args_opt_empty(p):
    'args_opt : '
    p[0] = ast.args_plus_cls()

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    p[1].addArgs(p[3])
    p[0] = p[1]
def p_args_single(p):
    'arg_plus : expr'
    p[0] = ast.args_plus_cls(p.linespan(0))
    p[0].addArgs(p[1])

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    p[0] = p[1]

#primary is an expr_wildcard
def p_field_access_dot(p):
    'field_access : primary DOT ID'
    p[0] = ast.FieldAccExpr(p[1], p[3])

#field_access here could be "real" field_access(1)
#                           or variable_access(2)
#                           or class_reference(3)
#according to instruction, will check in following order:
#                               (1) (2) (3) (1 again, assume it will later declared in a field)
def p_field_access_id(p):
    'field_access : ID'
#TODO: check scope rightaway or fill it up after AST construction?
    p[0] = ast.FieldAccExpr(None, p[1])

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    p[0] = ast.ArryAccExpr(p.linespan(0), p[1], p[3])

def p_method_invocation(p):
#args_opt should be a list of expressions
    'method_invocation : field_access LPAREN args_opt RPAREN'
    p[0] = ast.MethodInvExpr(p.linespan(0),p[1], p[1].getAccessId(), p[3])

#assign here has two possible types: assnexpr and autoexpr
def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0] = p[1]

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
    '''
    p[0] = ast.BinaryExpr(p.linespan(0), p[1], p[2], p[3])
def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    p[0] = ast.UnaryExpr(p.linespan(0), p[2], p[1])

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = ast.AssnExpr(p.linespan(0), p[1], p[3])
def p_assign_post(p):
    '''assign : lhs INC
              | lhs DEC'''
    p[0] = ast.AutoExpr(p.linespan(0), p[1], p[2], 'Post')
def p_assign_pre(p):
    '''assign : INC lhs
            | DEC lhs'''
    p[0] = ast.AutoExpr(p.linespan(0), p[2], p[1], 'Pre')

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    p[4].append(p[2])#[array, array, ..., array].append(baseTYpe)
    p[0] = ast.NewArryExpr(p[4], p[3],p.linespan(0))

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    p[0] = p[1] + p[2]

def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    p[0] = p[1]

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    p[0] = [p[2]]


def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    p[1].append('array')
    p[0] = p[1]
def p_dim_star_empty(p):
    'dim_star : '
    p[0] = []


# TODO:
def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0] = ast.StmtExprStmt(p[1])

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0] = p[1]

def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    p[0] = ast.SkipStmt(p.linespan(0))

def p_expr_opt(p):
    'expr_opt : expr'
    p[0] = p[1]
def p_expr_empty(p):
    'expr_opt : '
    p[0] = ast.EmptyExpr(p.linespan(0))

#expression over

# handle scope inc/dec
def p_scope_inc(p):
    'scope_inc: '
    scope += 1
def p_scope_dec(p):
    'scope_dec: '
    scope -= 1


def p_error(p):
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            parser.parse(f.read(), lexer=lex.lex(module=decaflexer), tracking=True, debug=None)
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), tracking=True, debug=1)

    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")
