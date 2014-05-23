import sys
import subprocess
import plistlib
import json

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
    f = open(sys.argv[1], 'r')
    contents = f.read()

    unpackage_theme(contents)
