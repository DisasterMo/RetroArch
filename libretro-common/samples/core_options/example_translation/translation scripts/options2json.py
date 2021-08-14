#!/usr/bin/env python3

# Convert core_options_us.h to core_options_us.json
# Usage: ./options2json.py msg_has_us.h

import re
import sys
import json

try:
    h_filename = sys.argv[1]
    json_filename = h_filename[:-2] + '.json'
except IndexError:
    print("Error with input (options2json)!")
    sys.exit(1)

p = re.compile(r'([A-Z_][A-Z0-9_]+)\s*(\"(?:"\s*"|\\\s*|.)*\")')

if __name__ == '__main__':
    try:
        with open(h_filename, 'r+', encoding='utf-8') as h_file:
            text = h_file.read()
            result = p.finditer(text)
            messages = {}
            for msg in result:
                key, val = msg.group(1, 2)
                if key not in messages:
                    if key and val:
                        # unescape & remove "\n"
                        messages[key] = re.sub(r'"\n\s*"', '\\\n', val[1:-1].replace('\\\"', '"'))
                else:
                    print(f"DUPLICATE KEY in {h_filename}: {key}")
            try:
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(messages, json_file, indent=2)
            except EnvironmentError:
                print('Error with creating/writing to ' + json_filename)
                sys.exit(1)
    except EnvironmentError:
        print('Error with opening/reading ' + h_filename)
