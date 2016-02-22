#!/usr/bin/python
import sys, os
from decafparser import parser

try:
    filename = sys.argv[1];
except IndexError:
    filename = "test_files/test_helloworld.dc"

inFile = open(str(filename))
inbuf = inFile.read()
result = parser.parse(inbuf, debug = 1)
print(result)
os.system("rm *.pyc");
