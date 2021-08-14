#!/usr/bin/env python3

"""Core options text extractor

The purpose of this script is to automatically generate 'libretro_core_options_intl.h' from 'libretro_core_options.h'
using translations from crowdin.

Both v1 and v2 structs are supported. It is, however, recommended to convert v1 files to v2 using the included
'v1_to_v2_converter.py'.

Usage:
Place this script, as well as the accompanying files, into the folder containing 'libretro_core_options.h' and run it.

This script will:
1.) create key words for & extract the relevant texts from libretro_core_options.h & save them into <core_name>_us.h
2.) sync those texts with crowndin & download available translations (if you have the proper permissions that is)
4.) (re-)create libretro_core_options_intl.h with the new translations

For more details see translation_readme.txt
"""
import core_option_regex as cor
import re
import sys
import os
import subprocess

dir_path = os.path.dirname(os.path.realpath(__file__))
if os.name == 'nt':
    joiner = '\\'
    python_call = 'python'
else:
    joiner = '/'
    python_call = 'python3'

# The core name provided at first run will be inserted here - the script will become 'core specific'
core_name = ''

on_offs = {'"enabled"', '"disabled"', '"true"', '"false"', '"on"', '"off"'}
special_chars = [chr(unicode) for unicode in list(range(33, 48)) + list(range(58, 65)) + list(range(91, 95)) + [96]
                 + list(range(123, 127))]

h_file_path = joiner.join((dir_path, 'libretro_core_options.h'))
intl_filename = joiner.join((dir_path, 'libretro_core_options_intl.h'))
crowdin_file_path = joiner.join((dir_path, core_name + '_us.h'))

main_text = ''

# intl_files = {
#     'ARABIC': f'core_options_ar.h',
#     'ASTURIAN': f'core_options_ast.h',
#     'CHINESE_SIMPLIFIED': f'core_options_chs.h',
#     'CHINESE_TRADITIONAL': f'core_options_cht.h',
#     'DUTCH': f'core_options_nl.h',
#     # 'ENGLISH': f'msg_hash_{filename[:]}.h',
#     'ESPERANTO': f'core_options_eo.h',
#     'FINNISH': f'core_options_fi.h',
#     'FRENCH': f'core_options_fr.h',
#     'GERMAN': f'core_options_de.h',
#     'GREEK': f'core_options_el.h',
#     'HEBREW': f'core_options_he.h',
#     'ITALIAN': f'core_options_it.h',
#     'JAPANESE': f'core_options_jp.h',
#     'KOREAN': f'core_options_ko.h',
#     'PERSIAN': f'core_options_fa.h',
#     'POLISH': f'core_options_pl.h',
#     'PORTUGUESE_BRAZIL': f'core_options_pt_br.h',
#     'PORTUGUESE_PORTUGAL': f'core_options_pt_pt.h',
#     'RUSSIAN': f'core_options_ru.h',
#     'SLOVAK': f'core_options_sk.h',
#     'SPANISH': f'core_options_es.h',
#     'TURKISH': f'core_options_tr.h',
#     'VIETNAMESE': f'core_options_vn.h'
# }


def create_intl_file():
    msg_dict = {}
    lang_up = ''

    def replace_pair(pair_match):
        offset = pair_match.start(0)
        if pair_match.group(1):
            if pair_match.group(2) in msg_dict:
                val = msg_dict[pair_match.group(2)] + lang_up
            elif pair_match.group(1) in msg_dict:
                val = msg_dict[pair_match.group(1)] + lang_up
            else:
                return pair_match.group(0)
        else:
            return pair_match.group(0)
        res = pair_match.group(0)[:pair_match.start(2) - offset] + val \
            + pair_match.group(0)[pair_match.end(2) - offset:]
        return res

    def replace_info(info_match):
        offset = info_match.start(0)
        if info_match.group(1) in msg_dict:
            res = info_match.group(0)[:info_match.start(1) - offset] + \
                  msg_dict[info_match.group(1)] + lang_up + \
                  info_match.group(0)[info_match.end(1) - offset:]
            return res
        else:
            return info_match.group(0)

    def replace_option(option_match):
        offset = option_match.start(0)
        if option_match.group(2):
            res = option_match.group(0)[:option_match.start(2) - offset] + msg_dict[option_match.group(2)] + lang_up
        else:
            return option_match.group(0)

        if option_match.group(3):
            res = res + option_match.group(0)[option_match.end(2) - offset:option_match.start(3) - offset]
            new_info = cor.p_info.sub(replace_info, option_match.group(3))
            res = res + new_info
        else:
            return option_match.group(0)

        if option_match.group(4):
            res = res + option_match.group(0)[option_match.end(3) - offset:option_match.start(4) - offset]
            new_pairs = cor.p_key_value.sub(replace_pair, option_match.group(4))
            res = res + new_pairs + option_match.group(0)[option_match.end(4) - offset:]
        else:
            res = res + option_match.group(0)[option_match.end(3) - offset:]

        return res

    if os.path.isfile(intl_filename):
        import shutil
        shutil.copy(intl_filename, intl_filename + '.old')

    with open(intl_filename, 'w', encoding='utf-8') as intl:  # libretro_core_options_intl.h
        out_txt = '#ifndef LIBRETRO_CORE_OPTIONS_INTL_H__\n' \
                  '#define LIBRETRO_CORE_OPTIONS_INTL_H__\n' \
                  '\n' \
                  '#if defined(_MSC_VER) && (_MSC_VER >= 1500 && _MSC_VER < 1900)\n' \
                  '/* https://support.microsoft.com/en-us/kb/980263 */\n' \
                  '#pragma execution_character_set("utf-8")\n' \
                  '#pragma warning(disable:4566)\n' \
                  '#endif\n' \
                  '\n' \
                  '#include <libretro.h>\n' \
                  '\n' \
                  '/*\n' \
                  ' ********************************\n' \
                  ' * VERSION: 2.0\n' \
                  ' ********************************\n' \
                  ' *\n' \
                  ' * - 2.0: Add support for core options v2 interface\n' \
                  ' * - 1.3: Move translations to libretro_core_options_intl.h\n' \
                  ' *        - libretro_core_options_intl.h includes BOM and utf-8\n' \
                  ' *          fix for MSVC 2010-2013\n' \
                  ' *        - Added HAVE_NO_LANGEXTRA flag to disable translations\n' \
                  ' *          on platforms/compilers without BOM support\n' \
                  ' * - 1.2: Use core options v1 interface when\n' \
                  ' *        RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION is >= 1\n' \
                  ' *        (previously required RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION == 1)\n' \
                  ' * - 1.1: Support generation of core options v0 retro_core_option_value\n' \
                  ' *        arrays containing options with a single value\n' \
                  ' * - 1.0: First commit\n' \
                  '*/\n' \
                  '\n' \
                  '#ifdef __cplusplus\n' \
                  'extern "C" {\n' \
                  '#endif\n' \
                  '\n' \
                  '/*\n' \
                  ' ********************************\n' \
                  ' * Core Option Definitions\n' \
                  ' ********************************\n' \
                  '*/\n\n'
        with open(crowdin_file_path, 'r+', encoding='utf-8') as template:  # <core_name>_us.h
            masked_msgs = cor.p_masked.finditer(template.read())
            for msg in masked_msgs:
                msg_dict[msg.group(2)] = msg.group(1)
        for file in os.listdir(dir_path):
            if file.startswith(core_name) and file.endswith('.h') \
                    and file != crowdin_file_path.replace(dir_path + joiner, ''):  # <core_name>_<lang>.h
                # all structs: group(0) full struct, group(1) beginning, group(2) content
                struct_groups = cor.p_struct.finditer(main_text)
                lang_up = file[:-2].replace(core_name, '').upper()
                lang_low = lang_up.lower()
                out_txt = out_txt + f'/* RETRO_LANGUAGE{lang_up}*/\n\n'
                with open(file, 'r+', encoding='utf-8') as f_in:
                    out_txt = out_txt + f_in.read() + '\n'
                for construct in struct_groups:
                    offset_construct = construct.start(0)
                    declaration = construct.group(1)
                    match = cor.p_type_name.search(declaration)
                    if match:
                        type_and_name = match.group(1, 2)
                    else:
                        print('Something is not right. Please make sure all structs are complete, '
                              'including the type and name declaration.')
                        sys.exit(1)
                    new_decl = re.sub(r'_us', lang_low, declaration)
                    start = construct.end(1) - offset_construct
                    end = construct.start(2) - offset_construct
                    out_txt = out_txt + new_decl + construct.group(0)[start:end]

                    content = construct.group(2)
                    new_content = cor.p_option.sub(replace_option, content)

                    start = construct.end(2) - offset_construct
                    out_txt = out_txt + new_content + construct.group(0)[start:] + '\n'

                if 'retro_core_option_definition' != type_and_name[0]:
                    out_txt = out_txt + f'struct retro_core_options_v2 options{lang_low}' \
                                        ' = {\n' \
                                        f'   option_cats{lang_low},\n' \
                                        f'   option_defs{lang_low}\n' \
                                        '};\n\n'
                os.remove(file)

        intl.write(out_txt + '\n#ifdef __cplusplus\n'
                             '}\n#endif\n'
                             '\n#endif')
    return None


def create_msg_hash(string_keyword_dict):
    try:
        with open(crowdin_file_path, 'w', encoding='utf-8') as crowdin_file:
            out_text = ''
            for string in string_keyword_dict:
                out_text = f'{out_text}{string_keyword_dict[string]} {string}\n'
            crowdin_file.write(out_text)
    except EnvironmentError:
        print(f'Error with creating/writing to {crowdin_file_path}!')
        sys.exit(1)


# def crowdin_sync():
#     from crowdin_api import CrowdinClient
#     try:
#         subprocess.run([python_call, 'options2json.py', crowdin_file_path])
#     except RuntimeError:
#         print('Error with subprocess call (crowdin_sync)!')
#         sys.exit(1)
#
#     api_token = input('Please provide Crowdin API token: ')
#
#     class FirstCrowdinClient(CrowdinClient):
#         TOKEN = api_token
#         TIMEOUT = 10  # Optional, sets http request timeout.
#         RETRY_DELAY = 0.1  # Optional, sets the delay between failed requests
#         MAX_RETRIES = 3  # Optional, sets the number of retries
#         HEADERS = {"Some-Header": ""}  # Optional, sets additional http request headers
#
#     client = FirstCrowdinClient()
#     projects = client.projects.list_projects()
#     with open('.'.join((crowdin_file_path[:-2], 'json')), 'r+', encoding='utf-8') as json_file:
#         storages_response = client.storages.add_storage(json_file)
#     if 'errors' in storages_response or 'error' in storages_response:
#         print(storages_response)
#         sys.exit(1)
#     strorage_id = storages_response['data']['id']
#     response = client.source_files.list_project_branches(projects['data'][0]['data']['id'])
#     return None


# --------------------          MAIN          -------------------- #

if __name__ == '__main__':
    if core_name == '':
        while core_name == '':
            core_name = input('Please enter the name of the core: ')
            for sp in special_chars:
                core_name = core_name.replace(sp, '')
        core_name = core_name.replace(' ', '_')
        with open(os.path.realpath(__file__), 'r', encoding='utf-8') as py_file:
            the_code = py_file.read()
        with open(os.path.realpath(__file__), 'w', encoding='utf-8') as py_file:
            py_file.write(re.sub(r"core_name = ''", f"core_name = '{core_name}'", the_code, 1))
    try:
        with open(h_file_path, 'r+', encoding='utf-8') as h_file:

            main_text = h_file.read()

            # all structs: group(0) full struct, group(1) beginning, group(2) content
            structs = cor.p_struct.finditer(main_text)
            str_n_hash = {}
            just_hash = set()
            for struct in structs:
                struct_declaration = struct.group(1)
                struct_match = cor.p_type_name.search(struct_declaration)
                if struct_match:
                    struct_type_name = struct_match.group(1, 2)
                else:
                    print('ERROR: No/incomplete struct declaration found!\n'
                          'Please make sure all structs are complete, including the type and name declaration.')
                    sys.exit(1)

                is_v2 = False
                if 'retro_core_option_v2_definition' == struct_type_name[0]:
                    is_v2 = True

                struct_content = struct.group(2)
                # 0: full option; 1: key; 2: description; 3: additional info; 4: key/value pairs
                struct_options = cor.p_option.finditer(struct_content)
                for i, option in enumerate(struct_options):
                    # group 1: key
                    if option.group(1):
                        key = option.group(1)
                        # no special chars allowed in key
                        for sp in special_chars:
                            key = key.replace(sp, '')
                        key = key.upper().replace(' ', '_')
                    else:
                        print(f'ERROR: No key found in struct {struct_type_name[1]} option {i}!')
                        sys.exit(1)

                    # group 2: description0
                    if option.group(2):
                        desc0 = option.group(2)
                        if desc0 not in str_n_hash:
                            h = re.sub(r'__+', '_', f'{key}_LABEL')
                            if h in just_hash:
                                n = 0
                                h = h + '_O' + str(i)
                                h_end = len(h)
                                while h in just_hash:
                                    h = h[:h_end] + '_' + str(n)
                                    n += 1
                            str_n_hash[desc0] = h
                            just_hash.add(h)
                    else:
                        print(f'ERROR: No label found in struct {struct_type_name[1]} option {option.group(1)}!')
                        sys.exit(1)

                    # group 3: desc1, info0, info1, category
                    if option.group(3):
                        option_info = cor.p_info.finditer(option.group(3))
                        if is_v2:
                            desc1 = next(option_info).group(1)
                            if 2 < len(desc1) and desc1 != 'NULL' and desc1 not in str_n_hash:
                                h = re.sub(r'__+', '_', f'{key}_LABEL_CAT')
                                if h in just_hash:
                                    n = 0
                                    h = h + '_O' + str(i)
                                    h_end = len(h)
                                    while h in just_hash:
                                        h = h[:h_end] + '_' + str(n)
                                        n += 1
                                str_n_hash[desc1] = h
                                just_hash.add(h)
                            for j, info in enumerate(option_info):
                                last = info.group(1)
                                if 2 < len(last) and last != 'NULL' and last not in str_n_hash:
                                    h = re.sub(r'__+', '_', f'{key}_INFO_{j}')
                                    if h in just_hash:
                                        n = 0
                                        h = h + '_O' + str(i)
                                        h_end = len(h)
                                        while h in just_hash:
                                            h = h[:h_end] + '_' + str(n)
                                            n += 1
                                    str_n_hash[last] = h
                                    just_hash.add(h)
                            if last in str_n_hash:  # category key should not be translated
                                str_n_hash.pop(last)
                                just_hash.remove(h)
                        else:
                            for j, info in enumerate(option_info):
                                gr1 = info.group(1)
                                if 2 < len(gr1) and gr1 != 'NULL' and gr1 not in str_n_hash:
                                    h = re.sub(r'__+', '_', f'{key}_INFO_{j}')
                                    if h in just_hash:
                                        n = 0
                                        h = h + '_O' + str(i)
                                        h_end = len(h)
                                        while h in just_hash:
                                            h = h[:h_end] + '_' + str(n)
                                            n += 1
                                    str_n_hash[gr1] = h
                                    just_hash.add(h)
                    else:
                        print(f'ERROR: Too few arguments in struct {struct_type_name[1]} option {option.group(1)}!')
                        sys.exit(1)

                    # group 4:
                    if option.group(4):
                        for j, kv_set in enumerate(cor.p_key_value.finditer(option.group(4))):
                            key, value = kv_set.group(1, 2)
                            if 2 > len(value) or value == 'NULL' or value in on_offs:
                                if 2 > len(key) or key == 'NULL' or key in on_offs:
                                    continue
                                value = key
                            if value not in str_n_hash and not value[1:-1].replace('+', '').replace('-', '').isdigit():
                                clean_value = value.encode('ascii', errors='ignore').decode('unicode-escape')
                                for sp in special_chars:
                                    clean_value = clean_value.replace(sp, '')
                                clean_value = clean_value.upper().replace(' ', '_')
                                h = re.sub(r'__+', '_', f"OPTION_VAL_{clean_value}")
                                if h in just_hash:
                                    n = 0
                                    h = h + '_O' + str(i)
                                    h_end = len(h)
                                    while h in just_hash:
                                        h = h[:h_end] + '_' + str(n)
                                        n += 1
                                str_n_hash[value] = h
                                just_hash.add(h)

            create_msg_hash(str_n_hash)
    except EnvironmentError:
        print(f'ERROR: Could not find/open {h_file_path}!')
        sys.exit(1)

    try:
        subprocess.run([python_call, 'crowdin_sync.py', core_name])
    except RuntimeError:
        sys.exit(2)
    try:
        while True:
            u_inp = input('Construct libretro_core_options_intl.h? A back-up will be created. (y/n)\n')
            if u_inp == 'y' or u_inp == 'yes':
                print('Constructing libretro_core_options_intl.h')
                create_intl_file()
                break
            elif u_inp == 'n' or u_inp == 'no':
                break
            else:
                print('Invalid input! Try again.')
    except RuntimeError:
        sys.exit(1)

