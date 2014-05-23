OSX Terminal Themer
===================

Manipulate OS X terminal theme files (.terminal).

- Convert between terminal format and json
- Set specific values from the commandline

---

    usage: osxterminalthemer.py [-h] [--convert {json,terminal}]
                                     [--set SET_VARS]
                                     [in_file]

      in_file
        Optionally provide input file name instead of 
        feeding to stdin

      --convert {json,terminal} 
        Convert input to the indicated format
      --set SET_VARS
        Set specific value from commandline.
        Follow format k="v" to set key k as value v.
        (See description for accepted keys)
        
    example:
      python osxterminalthemer.py --convert json < theme.terminal
      
      python osxterminalthemer.py \
        --set blackColor="0.0 0.0 0.0" \
        --set blueColor="0.0 0.0 0.5"           

