#!/usr/bin/python
import os
import argparse
from decafparser import decaf_parser

arg_parser = argparse.ArgumentParser(description='Decaf language checker')
arg_parser.add_argument('filename', help='file to compile')
arg_parser.add_argument('-d', action='store_true', help='enable debug mode')
args = arg_parser.parse_args()

if not args.filename:
    filename = "test_files/test_helloworld.dc"
inFile = open(args.filename)
inbuf = inFile.read()
inFile.close()
decaf_parser.parse(inbuf, debug=args.d)
try:
    os.system("rm *.pyc");
except:
    pass
