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

def unpackage_theme(pl_string):
    theme_pl = plistlib.readPlistFromString(pl_string)

    # Extract plist for each encoded key/value
    for k,v in theme_pl.iteritems():
        if k not in bplist_keys:
            continue

        # Convert complex entries (bplists) into xml
        theme_pl[k] = bplist_to_xml(v.data)
        theme_pl[k] = plistlib.readPlistFromString(theme_pl[k])

        # Also strip plistlib.Data for json output
        recursive_unwrap_data(theme_pl[k])

    return json.dumps(theme_pl, indent=4)

def recursive_wrap_data(plist):
    # Wrap any NSData objects in plistlb.data for plistlib write
    plist_iter = lambda x: x if isinstance(x, dict) else range(len(x))
    
    for key in plist_iter(plist):
        if key == 'data' or key in bplist_keys:
            plist[key] = plistlib.Data(plist[key])
        elif isinstance(plist[key], dict) or isinstance(plist[key], list):
            recursive_wrap_data(plist[key])

def recursive_unwrap_data(plist):
    # Unpackage plistlib.Data to preserve json output
    plist_iter = lambda x: x if isinstance(x, dict) else range(len(x))
    
    for key in plist_iter(plist):
        if isinstance(plist[key], plistlib.Data):
            plist[key] = {'data': plist[key].data}
        elif isinstance(plist[key], dict) or isinstance(plist[key], list):
            recursive_unwrap_data(plist[key])


def repackage_theme(json_string):
    theme_json = json.loads(json_string)

    # For each encoded key/value pair, rewrite plist
    # Encoded in binary, and encapsulate in plist.data object
    for k,v in theme_json.iteritems():
        if k not in bplist_keys:
            continue

        # Convert any data objects to plistlib.data
        recursive_wrap_data(v)

        v_plist = plistlib.writePlistToString(v)
        v_plist = xml_to_bplist(v_plist)
        theme_json[k] = v_plist
    
    recursive_wrap_data(theme_json)

    return plistlib.writePlistToString(theme_json)

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

        if args.convert == "terminal":
            print repackage_theme(in_data)
    
    # unpackage_theme(contents)
