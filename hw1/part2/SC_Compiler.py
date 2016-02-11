import Lexer
import Parser
import Symbols
import CodeEmit

class SC_Compier:
    """Top level class to assemble the compiling pipeline"""
    def __init__(self, lexer, parser, code_emitter, symTab):
        self.__lexer = lexer
        self.__parser = parser
        self.__code_emitter = code_emitter
        self.__symtab = symTab

    def startPipeline(self):
        self.__lexer.getNextToken()
        while self.__lexer.CurTok.getTokName() != 'TokEOF':
            ast = self.__parser.parse()
            self.__code_emitter.emitCode(ast)




if __name__ == '__main__':
    lexer = Lexer.Lexer('test_input')#default src location is stdin
    parser = Parser.Parser(lexer)
    sym_tab = Symbols.SymTab()
    code_emitter = CodeEmit.CodeEmitter(sym_tab)
    compiler = SC_Compier(lexer, parser, code_emitter, sym_tab)
    compiler.startPipeline()


