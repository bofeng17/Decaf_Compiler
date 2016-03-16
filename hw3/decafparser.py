#!/usr/bin/python

import ply.yacc as yacc
import decaflexer
from decaflexer import tokens
#from decaflexer import errorflag
from decaflexer import lex
import ast

import sys
import logging
from operator import add

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
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)


def init():
    decaflexer.errorflag = False

start = 'class_body_decl'

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
    ast.ClassRecord(p[2], p[3], p[5][0], p[5][1], p[5][2])
    for i in range(1, 3):
        for record in p[5][i]: # record: each MethodRecord/FieldRecord
            record.setContainingCls(p[2]) # set ContainingCls field

def p_class_decl_error(p):
    'class_decl : CLASS ID extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
    ast.ClassRecord(p[2], p[3], [], [], []) # empty CtorRecord/MethodRecord/FieldRecord list


def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0] = p[2] # p[2]: str of ID.lexeme
def p_extends_empty(p):
    ' extends : '
    p[0] = None # TODO: empty string or None?

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    p[0] = map(add, p[1], p[2])
def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0] = p[1]

# class_body_decl: [CtorRecord, MethodRecord, FieldRecord partial list(because we can declare more than one Fields at one time)]
def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0] = [[], [], p[1]]
def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0] = [[], [p[1]], []]
def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0] = [[p[1]], [], []]


# Field/Method/Constructor Declarations
def p_field_decl(p):
    'field_decl : mod var_decl'
    p[0] = []
    for var in p[2]:
        # var_decl: [var1, var2, ...]
        # var: [fieldName, typeRecord(a list)]
        p[0].append(ast.FieldRecord(var[0], None, p[1][0], p[1][1], var[1]))

def p_method_decl_void(p):
    'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
    p[0] = ast.MethodRecord(p[3], None, p[1][0], p[1][1], "void", p[5].mergeRecordList(p[7][0]), p[7][1]) # TODO: verify last two
def p_method_decl_nonvoid(p):
    'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
    # TODO: verify last two
    # p[5]: VariableTable for all formals, needs to merge with VariableRecord for all locals
    # p[7]: [list of variableRecord, BlockStatement]
    p[0] = ast.MethodRecord(p[3], None, p[1][0], p[1][1], p[2], p[5].mergeRecordList(p[7][0]), p[7][1])

def p_constructor_decl(p):
    'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
    p[0] = ast.CtorRecord(p[1][0], p[4].getAllFormals(), p[4].mergeRecordList(p[6][0]), p[6][1]) # TODO: verify last two



def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0] = [p[1],p[2]]

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

def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    for var in p[2]:
        var[1].append(p[1])
        # var[1]: type(list) of var, e.g. [array, array, int]
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

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[1].append(p[3])
    p[0] = p[1]
def p_var_list_single(p):
    'var_list : var'
    p[0] = [p[1]]

def p_var_id(p):
    'var : ID'
    # var: [fieldName, typeRecord(a list)]
    p[0] = [p[1], ast.TypeRecord()]
def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    p[1][1].append("array")
    p[0] = p[1]

def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = p[1]
def p_param_list_empty(p):
    'param_list_opt : '
    p[0] = None # TODO: pass an empty VariableTable or None?

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[3].setVarId(p[1].assignId())
    p[1].AddVar(p[3])
    p[0] = p[1]
def p_param_list_single(p):
    'param_list : param'
    p[0] = ast.VariableTable()
    p[1].setVarId(p[0].assignId())
    p[0].AddVar(p[1])

def p_param(p):
    'param : type var'
    p[2][1].append(p[1])
    p[0] = ast.VariableRecord(p[2][0], None, 'formal', p[2][1])


# Statements

def p_block(p):
    'block : LBRACE stmt_list RBRACE'
    # TODO: stub
    p[0] = [[],0]
def p_block_error(p):
    'block : LBRACE stmt_list error RBRACE'
    # error within a block; skip to enclosing block
    pass

def p_stmt_list_empty(p):
    'stmt_list : '
    pass
def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    pass


def p_stmt_if(p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt
          | IF LPAREN expr RPAREN stmt'''
    pass
def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    pass
def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    pass
def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    pass
def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    pass
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    pass
def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    pass
def p_stmt_block(p):
    'stmt : block'
    pass
def p_stmt_var_decl(p):
    'stmt : var_decl'
    pass
def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    pass
def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    pass
def p_literal_string_const(p):
    'literal : STRING_CONST'
    pass
def p_literal_null(p):
    'literal : NULL'
    pass
def p_literal_true(p):
    'literal : TRUE'
    pass
def p_literal_false(p):
    'literal : FALSE'
    pass

def p_primary_literal(p):
    'primary : literal'
    pass
def p_primary_this(p):
    'primary : THIS'
    pass
def p_primary_super(p):
    'primary : SUPER'
    pass
def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    pass
def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    pass
def p_primary_lhs(p):
    'primary : lhs'
    pass
def p_primary_method_invocation(p):
    'primary : method_invocation'
    pass

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    pass
def p_args_opt_empty(p):
    'args_opt : '
    pass

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    pass
def p_args_single(p):
    'arg_plus : expr'
    pass

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    pass

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    pass
def p_field_access_id(p):
    'field_access : ID'
    pass

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    pass

def p_method_invocation(p):
    'method_invocation : field_access LPAREN args_opt RPAREN'
    pass

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    pass
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
    pass
def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    pass

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    pass
def p_assign_post_inc(p):
    'assign : lhs INC'
    pass
def p_assign_pre_inc(p):
    'assign : INC lhs'
    pass
def p_assign_post_dec(p):
    'assign : lhs DEC'
    pass
def p_assign_pre_dec(p):
    'assign : DEC lhs'
    pass

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    pass

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    pass
def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    p[0] = 1

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    pass

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    pass
def p_dim_star_empty(p):
    'dim_star : '
    pass

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    pass

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    pass
def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    pass

def p_expr_opt(p):
    'expr_opt : expr'
    pass
def p_expr_empty(p):
    'expr_opt : '
    pass

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
            parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=None)
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=1)

    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")
