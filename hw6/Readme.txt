README.txt:

*Plus since hw5:
1)This compiler has SSA support, 
inside absmc.py  convert_to_SSA function

2)analyses.py
Reaching definition
Dominator tree+immediate dominator analysis
liveness analyses

3)inside codegen.py are the data structures of intermediate code
IR, PHI-NODE, BasicBlock, IR_Method


4)Register allocation uses the optimal allocation inherited by SSA code nature

5)Instrction selection translate the IR with regs allocated into MIPS code

6)Only static data are allocated in .data section, new object and new array are allocated using sbrk()









decaflexer.py	PLY/lex specification of Decaf tokens.
		Also defines "errorflag" used to signal error during scanning/parsing.
decafparser.py	PLY/yacc specification of Decaf grammar.
		The encoded grammar rules appear in the same order as in decaf manual.
		Defines "from_file" function that takes a file name
		and parses that file's contents. "from_file" returns
		True if no error, and False if error.

ast.py		Class structure and functions for AST construction and type checking

decafc.py	Driver: processes arguments and gets file name to pass
		to decafparser.from_file
		Decaf programs are assumed to be in files with ".decaf" suffix.
		Argument given to decafch may omit this suffix; e.g.
				python decafch test
		will read from test.decaf.

typecheck.py: 	the type checker that provides the important typechecking helper functions 
		including:  is_sub_type(), resolve_field(), resolve_method(), resolve_ctor()
           	and method overloading rules enforcements

codegen.py:	code to generate code

absmc.py:	code for abstract machine


Note:
main method must be public static int main(), and will be automatically add a 
__main__ label at the begin of the code. Like other static method, main method
cannot call instance methods. 
