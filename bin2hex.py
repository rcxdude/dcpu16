#!/usr/bin/env python3
#reinvent the wheel a bit, but it's dead simple
import sys
import utils

if len(sys.argv) != 2:
    print("usage: bin2hex.py [bin or hex file]")
    exit(1)

filename = sys.argv[1]

root,suffix = filename.rsplit(".",1)

if suffix == "hex":
    ifile = open(filename,"r")
    bytelist = []
    for word in utils.hex_to_words(ifile.read()): 
        bytelist.append(word & 0xff)
        bytelist.append((word & 0xff00) >> 8)
    ofile = open(root + ".bin","wb")
    ofile.write(bytes(bytelist))

if suffix == "bin":
    ifile = open(filename,"rb")
    ibytes = ifile.read()
    wordlist = []
    for wordchunk in utils.chunk(ibytes,2):
        wordlist.append(wordchunk[0] | wordchunk[1] << 8)
    ofile = open(root + ".hex", "w")
    ofile.write(utils.words_to_hex(wordlist))
