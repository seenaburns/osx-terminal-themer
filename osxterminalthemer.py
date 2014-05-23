"""

DESCRIPTION
  Manipulate OS X Terminal's theme files (.terminal file extension). 

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
    # Setup argument parser
    # Set formatter class to be RawTextHelper with wider fill to format
    #   usage text properly (enable __doc__ newlines, wider printing)
    parser = argparse.ArgumentParser(
        description=__doc__,
        prog='osxterminalthemer.py',
        formatter_class= \
          lambda prog: argparse.RawTextHelpFormatter(prog,2,72))
    parser.add_argument(
        "--convert",
        type=str,
        default=None,
        choices=["json", "terminal"],
        help='Convert input to the indicated format')
    parser.add_argument(
        "in_file",
        type=str,
        nargs='?',
        default=None,
        help="Optionally provide input file name instead of \n" +
             "feeding to stdin")
    parser.add_argument(
        '--set',
        action='append',
        dest='set_vars',
        default=None,
        help="Set specific value from commandline.\n" + \
             "Follow format k=\"v\" to set key k as value v.\n" + \
             "(See description for accepted keys)")

    args = parser.parse_args()

    # Fail if no action specified
    if (args.convert is None) and (args.set_vars is None):
        print 'No action specified! (convert or set)\n'
        parser.print_help()
        sys.exit()

    # Extract contents either from input file or stdin
    in_data = ""
    if args.in_file is not None:
        with open(args.in_file, 'r') as f:
            in_data = f.read()
    else:
        in_data = sys.stdin.read()

    if args.convert is not None:
        if args.convert == "json":            
            print unpackage_theme(in_data)
    
    # unpackage_theme(contents)
