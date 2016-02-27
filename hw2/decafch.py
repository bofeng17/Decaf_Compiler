#!/usr/bin/python
import os
import argparse
from decafparser import decaf_parser

arg_parser = argparse.ArgumentParser(description='Decaf language checker')
arg_parser.add_argument('filename', help='file to compile')
arg_parser.add_argument('-d', action='store_true', help='enable debug mode')
arg_parser.add_argument('-c', action='store_true', help='clean up intermediate files')
args = arg_parser.parse_args()

try:
    inFile = open(args.filename)
    inbuf = inFile.read()
    inFile.close()
    if len(inbuf) <= 0:
        print "empty file"
    else:
        decaf_parser.parse(inbuf, debug=args.d)
        if args.c:
            os.system("rm *.pyc");

except IOError:
    print args.filename+ ' not exist'
