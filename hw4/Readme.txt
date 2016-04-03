Example implementation of Decaf AST builder.	
Report errors to Yuxuan Shui and C. R. Ramakrishnan

README.txt:	this file
decaflexer.py	PLY/lex specification of Decaf tokens.
		Also defines "errorflag" used to signal error during scanning/parsing.
decafparser.py	PLY/yacc specification of Decaf grammar.
		The encoded grammar rules appear in the same order as in decaf manual.
		Defines "from_file" function that takes a file name
		and parses that file's contents. "from_file" returns
		True if no error, and False if error.

ast.py		Class structure and functions for AST construction.

decafch.py	Driver: processes arguments and gets file name to pass
		to decafparser.from_file
		Decaf programs are assumed to be in files with ".decaf" suffix.
		Argument given to decafch may omit this suffix; e.g.
				python decafch test
		will read from test.decaf.

typecheck.py: the type checker that provides the important typechecking helper functions
    including:  is_sub_type(), resolve_field(), resolve_method(), resolve_ctor()
            and method overloading rules enforcements


in hw4, all the stmts and exprs in ast.py are added function resolveType() to resolve the type of the stmt/expr and store it in a new field, expr_type

