"""
Manipulate OS X Terminal's theme files (.terminal file
extension). 

- Convert .terminal plist format and a decoded json format
- Set specific settings from the command line

"""

import sys
import subprocess
import plistlib
import json
import argparse

bplist_keys = ['ANSIBlackColor',
               'ANSIBlueColor',
               'ANSICyanColor',
               'ANSIGreenColor',
               'ANSIMagentaColor',
               'ANSIRedColor',
               'ANSIWhiteColor',
               'ANSIYellowColor',
               'ANSIBrightBlackColor',
               'ANSIBrightBlueColor',
               'ANSIBrightCyanColor',
               'ANSIBrightGreenColor',
               'ANSIBrightMagentaColor',
               'ANSIBrightRedColor',
               'ANSIBrightWhiteColor',
               'ANSIBrightYellowColor',
               'BackgroundColor',
               'SelectionColor',
               'TextColor',
               'TextBoldColor',
               'CursorColor',
               'Font']

def unpackage_theme(pl_string):
    theme_pl = plistlib.readPlistFromString(pl_string)
    
    # Extract plist for each encoded key/value
    for k,v in theme_pl.iteritems():
        if k not in bplist_keys:
            continue

        bplist = bplist_to_xml(v.data)
        theme_pl[k] = plistlib.readPlistFromString(bplist)

    return json.dumps(theme_pl, default=lambda o: o.__dict__, indent=4)
    
def bplist_to_xml(data):
    cmd = "plutil -convert xml1 - -o -"
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdin.write(data)
    stdout, stderr = p.communicate()

    return stdout

def xml_to_bplist(data):
    cmd = "plutil -convert binary1 - -o -"
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdin.write(data)
    stdout, stderr = p.communicate()

    return stdout

if __name__ == '__main__':
    convert = None
    set_vars = None
    description=__doc__
    parser = argparse.ArgumentParser(
        description=description,
        prog='osxterminalthemer.py',
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,2,72))
    
    parser.add_argument("--convert", type=str,
                        default=None,
                        choices=["json", "terminal"],
                        help='Convert input to the indicated format')
    # parser.add_argument("in_file", type=str, nargs='?',
    #                    help="Input file name")
    parser.add_argument('--set', action='append', dest='set_vars',
                        default=None,
                        help="Set specific value from commandline.\nFollow format k=\"v\" to set key k as value v.\n(See description for accepted keys)")
    args = parser.parse_args()

    if (convert is None) and (set_vars is None):
        print __doc__
        parser.print_help()
        sys.exit()
    
    print args

    # unpackage_theme(contents)
