import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from DECAFLexer import DECAFLexer

def p_empty(p):
    '''empty : '''
    pass

def p_program(p):
    '''program : program class_decl
               | empty'''
    # action here

def p_class_decl(p):
    '''class_decl : CLASS ID { class_body_decls }
                  | CLASS ID ( EXTENDS ID ) { class_body_decls }'''

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
    '''variables : variables , variable
                 | variable'''

def p_variable(p):
    '''variable : variable [ ]
                | ID'''

def p_method_decl(p):
    '''method_decl : modifier ( type | VOID ) ID ( formals ) block
                   | modifier ( type | VOID ) ID ( ) block'''

def p_constructor_decl(p):
    '''constructor_decl : modifier ID ( formals ) block
                        | modifier ID ( ) block'''

def p_formals(p):
    '''formals : formals , formal_param
               | formal_param'''

def p_formal_param(p):
    '''formal_param : type variable'''

def p_block(p):
    '''block : { stmts }'''

def p_stmts(p):
    '''stmts : stmts stmt
             | empty'''

def p_stmt(p): # the FOR statement is not finished for containing too many '?'
    '''stmt : IF ( expt ) stmt | IF ( expt ) stmt ELSE stmt
            | WHILE ( expr ) stmt
            | FOR ( stmt_expr ; expr ; stmt_expr ) stmt
            | RETURN exprs
            | stmt_expr
            | BREAK
            | CONTINUE
            | block
            | var_decl'''

def p_exprs(p):
    '''exprs : exprs expr
             | expr'''

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
        | ( expr )
        | NEW ID ( have_arguments )
        | lhs
        | method_invocation'''

def p_have_arguments(p):
    '''have_arguments : arguments
                      | empty'''

def p_arguments(p):
    '''arguments : arguments , expr
                 | expr'''
        
def p_lhs(p):
    '''lhs : field_access
        | array_access'''

def p_field_access(p):
    '''field_access : primary . ID
        | ID'''

def p_array_access(p):
    '''array_access : primary [ expr ]'''

def p_method_invocation(p):
    '''method_invocation : field_access ( have_arguments )'''

def p_expr(p):
    '''expr : primary
        | assign
        | new_array
        | expr arith_op expr
        | expr bool_op expr
        | unary_op expr'''

def p_assign(p):
    '''assign : lhs = expr
        | lhs INC
        | INC lhs
        | lhs DEC
        | DEC lhs'''

def p_new_array(p):
    '''new_array : new_array [ ]
                 | new_array_temp '''

def p_new_array_temp(p):
    '''new_array_temp : new_array_temp [ expr ]
                      | NEW type [ expr ]'''

def p_arith_op(p):
    '''arith_op : + | - | * | /'''

def p_bool_op(p):
    '''bool_op : AND | OR | EQL | UNEQL | < | > | LE | GE'''

def p_unary_op(p):
    '''unary_op: + | - | !'''

def p_stmt_expr(p):
    '''stmt_expr : assign
        | method_invocation'''

if __name__ == '__main__':
    # Build the parser
    parser = yacc.yacc()

    while True:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        print(result)
