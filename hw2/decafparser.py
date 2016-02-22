#!/usr/bin/python
import ply.yacc as yacc
import sys

# Get the token map from the lexer.  This is required.
from decaflexer import tokens

precedence = (
        ('right', '='),  # Nonassociative operators
        ('left', 'OR'),  # Nonassociative operators
        ('left', 'AND'),  # Nonassociative operators
        ('left', 'EQL', 'UNEQL'),  # Nonassociative operators
        ('nonassoc', '<', '>', 'LE', 'GE'),  # Nonassociative operators
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', '!', 'INC', 'DEC'),            # Unary minus operator

)

def p_program(p):
#    '''program : program class_decl
#        | empty'''
    '''program :  class_decl program
               | empty'''
    print 'program reduce success'
# action here

def p_class_decl(p):
    '''class_decl : CLASS ID '{' class_body_decls '}'
        | CLASS ID '(' EXTENDS ID ')' '{' class_body_decls '}' '''
    print 'class_decl'

def p_class_body_decls(p):
    '''class_body_decls : class_body_decls class_body_decl
        | class_body_decl'''

def p_class_body_decl(p):
    '''class_body_decl : field_decl
        | method_decl
        | constructor_decl'''

def p_field_decl(p):
    '''field_decl : modifier var_decl'''

def p_modifier(p):
    '''modifier : access class_member'''

def p_access(p):
    '''access : PUBLIC
        | PRIVATE
        |  empty'''

def p_class_member(p):
    '''class_member : STATIC
        | empty'''

def p_var_decl(p):
    '''var_decl : type variables'''

def p_type(p):
    '''type : INT
        | FLOAT
        | BOOLEAN
        | ID'''

def p_variables(p):
    '''variables : variables ',' variable
        | variable'''

def p_variable(p):
    '''variable : variable '[' ']'
        | ID'''

def p_method_decl(p):
    '''method_decl : modifier type ID '(' formals ')' block
        | modifier VOID ID '(' formals ')' block
        | modifier type ID '(' ')' block
        | modifier VOID ID '(' ')' block'''

#def p_all_type(p):
#    '''all_type : type
#        | VOID'''

def p_constructor_decl(p):
    '''constructor_decl : modifier ID '(' formals ')' block
        | modifier ID '(' ')' block'''

def p_formals(p):
    '''formals : formals ',' formal_param
        | formal_param'''

def p_formal_param(p):
    '''formal_param : type variable'''

def p_block(p):
    '''block : '{' stmts '}' '''

def p_stmts(p):
    '''stmts : stmts stmt
        | empty'''

def p_stmt(p): # the FOR statement is not finished for containing too many '?'
    '''stmt : IF '(' expr ')' stmt has_else
        | WHILE '(' expr ')' stmt
        | FOR '(' has_stmt_expr ';' has_expr ';' has_stmt_expr ')' stmt
        | RETURN has_expr ';'
        | stmt_expr ';'
        | BREAK ';'
        | CONTINUE ';'
        | block
        | var_decl
        | ';' '''

def p_has_else(p):
    '''has_else : ELSE stmt
                | empty'''

def p_has_stmt_expr(p):
    '''has_stmt_expr : stmt_expr
        | empty'''

def p_has_expr(p):
    '''has_expr : expr
        | empty'''

def p_literal(p):
    '''literal : INT_CONST
        | FLOAT_CONST
        | STRING_CONST
        | NULL
        | TRUE
        | FALSE'''

def p_primary(p):
    '''primary : literal
        | THIS
        | SUPER
        | '(' expr ')'
        | NEW ID '(' has_arguments ')'
        | lhs
        | method_invocation'''

def p_has_arguments(p):
    '''has_arguments : arguments
        | empty'''

def p_arguments(p):
    '''arguments : arguments ',' expr
        | expr'''

def p_lhs(p):
    '''lhs : field_access
        | array_access'''

def p_field_access(p):
    '''field_access : primary '.' ID
        | ID'''

def p_array_access(p):
    '''array_access : primary '[' expr ']' '''

def p_method_invocation(p):
    '''method_invocation : field_access '(' has_arguments ')' '''

def p_expr(p):
    '''expr : primary
        | assign
        | new_array
        | expr '+' expr
        | expr '-' expr
        | expr '*' expr
        | expr '/' expr
        | expr AND expr
        | expr OR expr
        | expr EQL expr
        | expr UNEQL expr
        | expr '<' expr
        | expr '>' expr
        | expr LE expr
        | expr GE expr
        | '+' expr %prec '!'
        | '-' expr %prec '!'
        | '!' expr '''

def p_assign(p):
    '''assign : lhs '=' expr
        | lhs INC
        | INC lhs
        | lhs DEC
        | DEC lhs'''

def p_new_array(p):
    '''new_array : new_array '[' ']'
        | new_array_temp '''

def p_new_array_temp(p):
    '''new_array_temp : new_array_temp '[' expr ']'
        | NEW type '[' expr ']' '''

#def p_arith_op(p):
#    '''arith_op : '+'
#        | '-'
#        | '*'
#        | '/' '''

#def p_bool_op(p):
#    '''bool_op : AND
#        | OR
#        | EQL
#        | UNEQL
#        | '<'
#        | '>'
#        | LE
#        | GE'''

#def p_unary_op(p):
#    '''unary_op : '+'
#        | '-'
#        | '!' '''

def p_stmt_expr(p):
    '''stmt_expr : assign
        | method_invocation'''

def p_empty(p):
    '''empty : '''
    pass

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

if __name__ == '__main__':
    # Build the parser

    parser = yacc.yacc()
    filename = sys.argv[1];
    inFile = open(str(filename))
    inbuf = inFile.read()
    result = parser.parse(inbuf, debug = 1)
    print(result)
else:
    parser = yacc.yacc()
