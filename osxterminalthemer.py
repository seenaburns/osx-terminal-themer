import sys
import subprocess
import plistlib

def unpackage_theme(pl_string):
    theme_pl = plistlib.readPlistFromString(pl_string)
    
    print theme_pl

if __name__ == '__main__':
    f = open(sys.argv[1], 'r')
    contents = f.read()

    unpackage_theme(contents)
