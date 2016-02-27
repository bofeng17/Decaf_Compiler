Team Member:
Yaohui Chen, Bo Feng
======================================================================

To run: 
do "./decafch.py file_name_to_check"
======================================================================

Grammar (in Backus-Naur Form): 
Words in UPPERCASE or single character stand for terminals, while words in lowercase stand for non_terminals
Grammar is augmented and S' is the actual start symbol. empty stands for empty sysbol (epsilon)

The regular expression-like notations in Extended Backus-Naur Form Grammar described in the ref. manual are transformed in these ways:
	For '*' or '+', we transform them into left-recursive grammar, which is prefered by LALR parser. For example, "program ::= class_decl*" is transformed into "program -> class_decl program | empty". There is one exception for "new_array ::= new type ([expr])+([])*", we transform ([])* into right recursive grammar to avoid shift-reduce conflict in an efficient way
	For '?', we add a new non-terminal sysbol named "has_xxx", For example, "stmt ::= for ( stmt_expr? ; expr? ; stmt_expr? ) stmt" is tranformed into "stmt -> FOR ( has_stmt_expr ; has_expr ; has_stmt_expr ) stmt" and "has_stmt_expr -> stmt | empty"

Rule 0     S' -> program
Rule 1     program -> class_decl program
Rule 2     program -> empty
Rule 3     class_decl -> CLASS ID { class_body_decls }
Rule 4     class_decl -> CLASS ID ( EXTENDS ID ) { class_body_decls }
Rule 5     class_body_decls -> class_body_decls class_body_decl
Rule 6     class_body_decls -> class_body_decl
Rule 7     class_body_decl -> field_decl
Rule 8     class_body_decl -> method_decl
Rule 9     class_body_decl -> constructor_decl
Rule 10    field_decl -> modifier var_decl
Rule 11    modifier -> access class_member
Rule 12    access -> PUBLIC
Rule 13    access -> PRIVATE
Rule 14    access -> empty
Rule 15    class_member -> STATIC
Rule 16    class_member -> empty
Rule 17    var_decl -> type variables
Rule 18    type -> INT
Rule 19    type -> FLOAT
Rule 20    type -> BOOLEAN
Rule 21    type -> ID
Rule 22    variables -> variables , variable
Rule 23    variables -> variable
Rule 24    variable -> variable [ ]
Rule 25    variable -> ID
Rule 26    method_decl -> modifier type ID ( formals ) block
Rule 27    method_decl -> modifier VOID ID ( formals ) block
Rule 28    method_decl -> modifier type ID ( ) block
Rule 29    method_decl -> modifier VOID ID ( ) block
Rule 30    constructor_decl -> modifier ID ( formals ) block
Rule 31    constructor_decl -> modifier ID ( ) block
Rule 32    formals -> formals , formal_param
Rule 33    formals -> formal_param
Rule 34    formal_param -> type variable
Rule 35    block -> { stmts }
Rule 36    stmts -> stmts stmt
Rule 37    stmts -> empty
Rule 38    stmt -> IF ( expr ) stmt has_else
Rule 39    stmt -> WHILE ( expr ) stmt
Rule 40    stmt -> FOR ( has_stmt_expr ; has_expr ; has_stmt_expr ) stmt
Rule 41    stmt -> RETURN has_expr ;
Rule 42    stmt -> stmt_expr ;
Rule 43    stmt -> BREAK ;
Rule 44    stmt -> CONTINUE ;
Rule 45    stmt -> block
Rule 46    stmt -> var_decl
Rule 47    stmt -> ;
Rule 48    has_else -> ELSE stmt
Rule 49    has_else -> empty
Rule 50    has_stmt_expr -> stmt_expr
Rule 51    has_stmt_expr -> empty
Rule 52    has_expr -> expr
Rule 53    has_expr -> empty
Rule 54    literal -> INT_CONST
Rule 55    literal -> FLOAT_CONST
Rule 56    literal -> STRING_CONST
Rule 57    literal -> NULL
Rule 58    literal -> TRUE
Rule 59    literal -> FALSE
Rule 60    primary -> literal
Rule 61    primary -> THIS
Rule 62    primary -> SUPER
Rule 63    primary -> ( expr )
Rule 64    primary -> NEW ID ( has_arguments )
Rule 65    primary -> lhs
Rule 66    primary -> method_invocation
Rule 67    has_arguments -> arguments
Rule 68    has_arguments -> empty
Rule 69    arguments -> arguments , expr
Rule 70    arguments -> expr
Rule 71    lhs -> field_access
Rule 72    lhs -> array_access
Rule 73    field_access -> primary . ID
Rule 74    field_access -> ID
Rule 75    array_access -> primary [ expr ]
Rule 76    method_invocation -> field_access ( has_arguments )
Rule 77    expr -> primary
Rule 78    expr -> assign
Rule 79    expr -> new_array
Rule 80    expr -> expr + expr
Rule 81    expr -> expr - expr
Rule 82    expr -> expr * expr
Rule 83    expr -> expr / expr
Rule 84    expr -> expr AND expr
Rule 85    expr -> expr OR expr
Rule 86    expr -> expr EQL expr
Rule 87    expr -> expr UNEQL expr
Rule 88    expr -> expr < expr
Rule 89    expr -> expr > expr
Rule 90    expr -> expr LE expr
Rule 91    expr -> expr GE expr
Rule 92    expr -> + expr
Rule 93    expr -> - expr
Rule 94    expr -> ! expr
Rule 95    assign -> lhs = expr
Rule 96    assign -> lhs INC
Rule 97    assign -> INC lhs
Rule 98    assign -> lhs DEC
Rule 99    assign -> DEC lhs
Rule 100   new_array -> new_array [ ]
Rule 101   new_array -> new_array_temp
Rule 102   new_array_temp -> NEW type [ expr ] new_array_temp2
Rule 103   new_array_temp2 -> [ expr ] new_array_temp2
Rule 104   new_array_temp2 -> empty
Rule 105   stmt_expr -> assign
Rule 106   stmt_expr -> method_invocation
Rule 107   empty -> <empty>

Along with precedence and associavity table:
precedence = (
        ('right', '='),  
        ('left', 'OR'),  
        ('left', 'AND'),  
        ('left', 'EQL', 'UNEQL'),  
        ('nonassoc', '<', '>', 'LE', 'GE'), 
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', '!', 'INC', 'DEC'), # '!' stands for all unary operators: {+, -, !}

)

======================================================================

Conflict:
1) In state 199: 
For ELSE, it can either shift along: (48) has_else -> . ELSE stmt, or reduce as: (107) empty -> .
The shift/reduce conflict is resolved as shift.

======================================================================