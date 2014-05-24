"""

DESCRIPTION
  Manipulate OS X Terminal's theme files (.terminal file extension). 

  - Convert .terminal plist format and a decoded json format
  - Set specific settings from the command line

"""
examples_doc = """
EXAMPLES
  python osxterminalthemer.py --convert json < theme.terminal

  python osxterminalthemer.py \\
    --set blackColor="0.0 0.0 0.0" \\
    --set blueColor="0.0 0.0 0.5"
"""

import sys
import subprocess
import plistlib
import json
import argparse

bplist_keys = [
    'ANSIBlackColor',
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
    'Font'
]

# Map accepted set keys to their key in json
# Font has special case
set_key_mapping = {
    'blackcolor': 'ANSIBlackColor',
    'bluecolor': 'ANSIBlueColor',
    'cyancolor': 'ANSICyanColor',
    'greencolor': 'ANSIGreenColor',
    'magentacolor': 'ANSIMagentaColor',
    'redcolor': 'ANSIRedColor',
    'whitecolor': 'ANSIWhiteColor',
    'yellowcolor': 'ANSIYellowColor',
    'brightblackcolor': 'ANSIBrightBlackColor',
    'brightbluecolor': 'ANSIBrightBlueColor',
    'brightcyancolor': 'ANSIBrightCyanColor',
    'brightgreencolor': 'ANSIBrightGreenColor',
    'brightmagentacolor': 'ANSIBrightMagentaColor',
    'brightredcolor': 'ANSIBrightRedColor',
    'brightwhitecolor': 'ANSIBrightWhiteColor',
    'brightyellowcolor': 'ANSIBrightYellowColor',
    'backgroundcolor': 'BackgroundColor',
    'selectioncolor': 'SelectionColor',
    'textcolor': 'TextColor',
    'textboldcolor': 'TextBoldColor',
    'cursorcolor': 'CursorColor',
    'font': 'Font'
}
set_keys_doc = """
--set keys

  COLORS
    Take format --set key="color" where color is an RGB float (0 to 1) value
    example: --set key="0.5 0.2 .03"

    %s

  FONTS
    Take format --set key="FontName Size"
    example: --set font="Monaco 10.0"

    font

""" % ('\n    '.join([x for x in set_key_mapping.keys() if 'color' in x]))



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

def wrap_data(plist):
    # Wrap any data objects in plistlb.data
    # Assumes unwrap_data ensures output format {'data': content}
    plist_iter = lambda x: x if isinstance(x, dict) else range(len(x))
    
    for key in plist_iter(plist):
        data = None
        if isinstance(plist[key], dict):
            data = plist[key].get('data', None)
        if data is not None:
            plist[key] = plistlib.Data(data)
        elif isinstance(plist[key], dict) or isinstance(plist[key], list):
            wrap_data(plist[key])

def unwrap_data(plist):
    # Recursively find plistlib.Data objects and turn them into
    # dicts with format {'data': content}
    plist_iter = lambda x: x if isinstance(x, dict) else range(len(x))
    
    for key in plist_iter(plist):
        if isinstance(plist[key], plistlib.Data):
            plist[key] = {'data': plist[key].data}
        elif isinstance(plist[key], dict) or isinstance(plist[key], list):
            unwrap_data(plist[key])


def unpackage_theme(pl_string):
    theme_pl = plistlib.readPlistFromString(pl_string)
    unwrap_data(theme_pl)

    # Extract plist for each bplist encoded key/value
    for k,v in theme_pl.iteritems():
        if k not in bplist_keys:
            continue
        v_plist = bplist_to_xml(v['data'])
        v_plist = plistlib.readPlistFromString(v_plist)
        unwrap_data(v_plist)
        theme_pl[k]['data'] = v_plist 

    return json.dumps(theme_pl, indent=4)

def repackage_theme(json_string):
    theme_json = json.loads(json_string)

    # For each encoded key/value pair, rewrite plist
    # Encoded in binary, and encapsulate in plist.data object
    for k,v in theme_json.iteritems():
        if k not in bplist_keys:
            continue

        # Convert any data objects to plistlib.data
        wrap_data(v['data'])

        v_plist = plistlib.writePlistToString(v['data'])
        v_plist = xml_to_bplist(v_plist)
        theme_json[k]['data'] = v_plist

    wrap_data(theme_json)

    return plistlib.writePlistToString(theme_json)

def set_values(json, args_set):
    # Change key value pairs of args_set in theme json
    # args_set is list of set commands of format k=v
    # 
    # On success: return None
    # On failure: error reason

    set_dict = {}
    for set_cmd in args_set:
        try:
            k, v = set_cmd.split('=')
            k = k.lower()
            set_dict[k] = v
        except Exception:
            return "'--set %s' bad format (should be k=v)" % (set_cmd)
    
        if k not in set_key_mapping.keys():
            return "'%s' not an accepted --set key, see --help" % (k)

    print set_dict

    return None

if __name__ == '__main__':
    # Setup argument parser
    # Set formatter class to be RawTextHelper with wider fill to format
    #   usage text properly (enable __doc__ newlines, wider printing)
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=set_keys_doc + examples_doc,
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
    thm_data = ""
    if args.in_file is not None:
        with open(args.in_file, 'r') as f:
            thm_data = f.read()
    else:
        thm_data = sys.stdin.read()

    # First set values in case both convert and set
    if args.set_vars is not None:
        tmp_thm_data = unpackage_theme(thm_data)

        set_return = set_values(tmp_thm_data, args.set_vars)
        if set_return is not None:
            print set_return
            sys.exit(1)

        thm_data = repackage_theme(tmp_thm_data)

    if args.convert is not None:
        if args.convert == "json":            
            thm_data = unpackage_theme(thm_data)

        if args.convert == "terminal":
            thm_data = repackage_theme(thm_data)
            
    sys.stdout.write(thm_data)
