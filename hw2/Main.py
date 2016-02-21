"""Token definition for ply.lex"""
#lexer.token() returns the next valid token on the input stream

from DECAFLexer import DECAFLexer

#10 //fwoejffwef
#
#    12 //fwoej ffwef
# Test it out
data = '''
    11 //fwoej\nffwef
    "w g"
    "fwlefj\"qe"
    "wefje\\of"
    13.2134 + int * 10
    + -20 *2
    '''
test1 = '''
    class hello_world{
        public static void main() {
            Out.print("Hello World!\n");
        }
    }
'''

test2 = '''
    class nrfib{
        public static void main() {
            int n, i, fn, fn_prev;
            n = In.scan_int();
            fn = 1;
            fn_1 = 0;
            for(i=1; i<n; i=i+1) {
                fn = fn_prev + fn;
                fn_prev = fn - fn_prev;
            }
            Out.print("Fib = ");
            Out.print(fn);
            Out.print("\n");
        }
    }
'''

# didn't test yet
test3 = '''
    class rfib{
        static int fib(int n) {
            if (n <= 2)
                return 1;
        }
        else
            return fib(n-1) + fib(n-2);
            
        public static void main() {
            int n;
            n = In.scan_int();
            Out.print("Fib = ");
            Out.print(fib(n));
            Out.print("\n");
        }
    }
'''

if __name__ == '__main__':

    lexer = DECAFLexer(test2)
    lexer.scan()
    lexer.test()