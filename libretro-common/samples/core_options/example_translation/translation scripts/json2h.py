#!/usr/bin/env python3

# Convert *.json to *.h
# Usage: ./json2h.py core_name_fr.json

import re
import sys
import json

try:
    json_filename = sys.argv[1]
    core_name = sys.argv[2]
    h_filename = json_filename.replace('.json', '.h')
    file_lang = json_filename.replace('.json', '').replace(core_name, '').upper()
except IndexError:
    print("Usage: ./json2h.py core_name_<language_postfix>.json core_name")
    sys.exit(1)

if json_filename == core_name + '_us.json':
    print('    skipped')
    sys.exit(0)

p = re.compile(r'([A-Z_][A-Z0-9_]+)\s*(\"(?:"\s*"|\\\s*|.)*\")')


def update(messages, template, source_messages):
    translation = template
    template_messages = p.finditer(template)
    for tp_msg in template_messages:
        old_key = tp_msg.group(1)
        old_msg = tp_msg.group(2)
        if old_key in messages and messages[old_key] != source_messages[old_key]:
            tp_msg_val = old_msg[1:-1]
            tl_msg_val = messages[old_key]
            tl_msg_val = tl_msg_val.replace('"', '\\\"').replace('\n', '')  # escape
            # Replace last match, in case the key contains the value string
            new_msg = old_msg.replace(tp_msg_val, tl_msg_val, 1)
            translation = re.sub(re.escape(old_key), '#define ' + old_key + file_lang, translation, 1)
            translation = re.sub(re.escape(old_msg), new_msg, translation, 1)
            # Remove English duplicates and non-translatable strings
        else:
            translation = re.sub(re.escape(old_key), '#define ' + old_key + file_lang, translation, 1)
            translation = re.sub(re.escape(old_msg), 'NULL', translation, 1)
    return translation


with open(core_name + '_us.h', 'r', encoding='utf-8') as template_file:
    template = template_file.read()
    with open(core_name + '_us.json', 'r+', encoding='utf-8') as source_json_file:
        source_messages = json.load(source_json_file)
        with open(json_filename, 'r+', encoding='utf-8') as json_file:
            messages = json.load(json_file)
            new_translation = update(messages, template, source_messages)
            with open(h_filename, 'w', encoding='utf-8') as h_file:
                h_file.seek(0)
                h_file.write(new_translation)
                h_file.truncate()
