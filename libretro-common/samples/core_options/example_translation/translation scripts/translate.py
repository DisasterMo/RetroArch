#!/usr/bin/env python3

"""Core options text extractor

The purpose of this script is to automatically generate 'libretro_core_options_intl.h' from 'libretro_core_options.h'
using translations from crowdin.

Both v1 and v2 structs are supported. It is, however, recommended to convert v1 files to v2 using the included
'v1_to_v2_converter.py'.

Usage:
Place this script, as well as the accompanying files, into the folder containing 'libretro_core_options.h'and
run it: python3 translate.py <Your Crowdin API token>

This script will:
1.) create key words for & extract the relevant texts from libretro_core_options.h & save them into <core_name>_us.h
2.) sync those texts with crowndin & download available translations (if you have the proper permissions that is)
4.) (re-)create libretro_core_options_intl.h with the new translations

For more details see translation_readme.txt
"""
# TODO: proper import of cor
import core_option_regex as cor
import re
import sys
import os

try:
    #_expected_args = 2
    _core_name = sys.argv[1]  # 'core_name'  #
    _api_token = sys.argv[2]  # Crowdin API v2 token
    # if _expected_args < len(sys.argv):
    #     _upload_translations = sys.argv[_expected_args]
    # else:
    #     _upload_translations = False
except IndexError:
    print('Please provide both core name & Crowdin API token!')
    sys.exit(1)
_project_id = 11111  # id of the crowdin project to sync with
_main_text = ''

if os.name == 'nt':
    _joiner = '\\'
else:
    _joiner = '/'

_dir_path = os.path.dirname(os.path.realpath(__file__))

# The core name provided at first run will be inserted here - the script will become 'core specific'

_langs_to_id = {'_ar': 'ar',
                '_ast': 'ast',
                '_chs': 'zh-CN',
                '_cht': 'zh-TW',
                '_cs': 'cs',
                '_cy': 'cy',
                '_da': 'da',
                '_de': 'de',
                '_el': 'el',
                '_eo': 'eo',
                '_es': 'es-ES',
                '_fa': 'fa',
                '_fi': 'fi',
                '_fr': 'fr',
                '_gl': 'gl',
                '_he': 'he',
                '_hu': 'hu',
                '_id': 'id',
                '_it': 'it',
                '_ja': 'ja',
                '_ko': 'ko',
                '_nl': 'nl',
                '_pl': 'pl',
                '_pt_br': 'pt-PT',
                '_pt_pt': 'pt-BR',
                '_ru': 'ru',
                '_sk': 'sk',
                '_sv': 'sv-SE',
                '_tr': 'tr',
                '_uk': 'uk',
                '_vn': 'vi'}
_on_offs = {'"enabled"', '"disabled"', '"true"', '"false"', '"on"', '"off"'}
_special_chars = [chr(unicode) for unicode in list(range(33, 48)) + list(range(58, 65)) + list(range(91, 95)) + [96]
                  + list(range(123, 127))]

_h_file_path = _joiner.join((_dir_path, 'libretro_core_options.h'))
_intl_file_path = _joiner.join((_dir_path, 'libretro_core_options_intl.h'))


def remove_special_chars(text):
    res = text
    for sp in _special_chars:
        res = res.replace(sp, '')
    return res


def get_struct_type_name(decl: str):
    struct_match = cor.p_type_name.search(decl)
    if struct_match:
        if struct_match.group(3):
            struct_type_name = struct_match.group(1, 2, 3)
        elif struct_match.group(4):
            struct_type_name = struct_match.group(1, 2, 4)
        else:
            struct_type_name = struct_match.group(1, 2)
    else:
        print('ERROR: No or incomplete struct declaration found!\n'
              'Please make sure all structs are complete, including the type and name declaration.')
        sys.exit(1)
    return struct_type_name


def create_intl_file(text, corename, file_path):
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

    if os.path.isfile(_intl_file_path):
        if not os.path.isfile(_intl_file_path + '.old'):
            import shutil
            shutil.copy(_intl_file_path, _intl_file_path + '.old')

    with open(_intl_file_path, 'w', encoding='utf-8') as intl:  # libretro_core_options_intl.h
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
        with open(file_path, 'r+', encoding='utf-8') as template:  # <core_name>_us.h
            masked_msgs = cor.p_masked.finditer(template.read())
            for msg in masked_msgs:
                msg_dict[msg.group(2)] = msg.group(1)
        for file in os.listdir(_dir_path):
            # <core_name>_<lang>.h
            if file.startswith(corename) and file.endswith('.h') and file != corename + '_us.h':
                # all structs: group(0) full struct, group(1) beginning, group(2) content
                struct_groups = cor.p_struct.finditer(text)
                lang_up = file[:-2].replace(corename, '').upper()
                lang_low = lang_up.lower()
                out_txt = out_txt + f'/* RETRO_LANGUAGE{lang_up}*/\n\n'
                with open(file, 'r+', encoding='utf-8') as f_in:
                    out_txt = out_txt + f_in.read() + '\n'
                for construct in struct_groups:
                    offset_construct = construct.start(0)
                    declaration = construct.group(1)
                    struct_type_name = get_struct_type_name(declaration)
                    if 3 > len(struct_type_name):
                        new_decl = re.sub(re.escape(struct_type_name[1]), struct_type_name[1] + lang_low, declaration)
                    else:
                        new_decl = re.sub(re.escape(struct_type_name[2]), lang_low, declaration)
                    start = construct.end(1) - offset_construct
                    end = construct.start(2) - offset_construct
                    out_txt = out_txt + new_decl + construct.group(0)[start:end]

                    content = construct.group(2)
                    new_content = cor.p_option.sub(replace_option, content)

                    start = construct.end(2) - offset_construct
                    out_txt = out_txt + new_content + construct.group(0)[start:] + '\n'

                if 'retro_core_option_definition' != struct_type_name[0]:
                    out_txt = out_txt + f'struct retro_core_options_v2 options{lang_low}' \
                                        ' = {\n' \
                                        f'   option_cats{lang_low},\n' \
                                        f'   option_defs{lang_low}\n' \
                                        '};\n\n'
                os.remove(file)

        intl.write(out_txt + '\n#ifdef __cplusplus\n'
                             '}\n#endif\n'
                             '\n#endif')
    return


def create_msg_hash(file_path, keyword_string_dict):
    files = {}
    for localisation in keyword_string_dict:
        files[localisation] = file_path + f'{localisation}.h'
        try:
            with open(files[localisation], 'w', encoding='utf-8') as crowdin_file:
                out_text = ''
                for keyword in keyword_string_dict[localisation]:
                    out_text = f'{out_text}{keyword} {keyword_string_dict[localisation][keyword]}\n'
                crowdin_file.write(out_text)
        except EnvironmentError:
            print(f'Error with creating/writing to {files[localisation]}!')
            sys.exit(1)
    return files


def options2json(file_paths):
    jsons = {}
    for file_lang in file_paths:
        jsons[file_lang] = file_paths[file_lang][:-2] + '.json'

        p = cor.p_masked

        try:
            with open(file_paths[file_lang], 'r+', encoding='utf-8') as h_file:
                text = h_file.read()
                result = p.finditer(text)
                messages = {}
                for msg in result:
                    key, val = msg.group(1, 2)
                    if key not in messages:
                        if key and val:
                            # unescape & remove "\n"
                            messages[key] = re.sub(r'"\s*(?:(?:/\*(?:.|[\r\n])*?\*/|//.*[\r\n]+)\s*)*"',
                                                   '\\\n', val[1:-1].replace('\\\"', '"'))
                    else:
                        print(f"DUPLICATE KEY in {file_paths[file_lang]}: {key}")
                try:
                    with open(jsons[file_lang], 'w', encoding='utf-8') as json_file:
                        json.dump(messages, json_file, indent=2)
                except EnvironmentError:
                    print('Error with creating/writing to ' + jsons[file_lang])
                    sys.exit(1)
        except EnvironmentError:
            print('Error with opening/reading ' + file_paths[file_lang])
            sys.exit(1)

    return jsons


def json2h(json_filename, core_name):
    h_filename = json_filename.replace('.json', '.h')
    file_lang = json_filename.replace('.json', '').replace(core_name, '').upper()

    if json_filename == core_name + '_us.json':
        print('    skipped')
        return

    p = cor.p_masked

    def update(s_messages, s_template, s_source_messages):
        translation = ''
        template_messages = p.finditer(s_template)
        for tp_msg in template_messages:
            old_key = tp_msg.group(1)
            if old_key in s_messages and s_messages[old_key] != s_source_messages[old_key]:
                tl_msg_val = s_messages[old_key]
                tl_msg_val = tl_msg_val.replace('"', '\\\"').replace('\n', '')  # escape
                translation = ''.join((translation, '#define ', old_key, file_lang, f' "{tl_msg_val}"\n'))

            else:  # Remove English duplicates and non-translatable strings
                translation = ''.join((translation, '#define ', old_key, file_lang, ' NULL\n'))
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
    return


def crowdin_upload_source(client, project_id, file_name, corename):
    with open(file_name, 'r+', encoding='utf-8') as json_file:
        storages_response = client.storages.add_storage(json_file)
    if 'errors' in storages_response or 'error' in storages_response:
        print(storages_response)
        sys.exit(1)
    storage_id = storages_response['data']['id']

    from crowdin_api.api_resources.source_files.types import GeneralExportOptions

    export = GeneralExportOptions(exportPattern=f'/{corename}_%osx_locale%.json')  # osx_code
    files_response = client.source_files.list_files(project_id)
    for f in files_response['data']:
        f = f['data']
        if f['name'] == corename + '_us.json':
            file_id = f['id']
            response = client.source_files.update_file(project_id, file_id, storage_id, exportOptions=export)
            return response
    response = client.source_files.add_file(project_id, storage_id, corename + '_us.json', exportOptions=export)
    return response


def crowdin_upload_translation(client, translation_file_path, project_id, language_id, corename):
    files_response = client.source_files.list_files(project_id)['data']
    with open(translation_file_path, 'r+', encoding='utf-8') as json_file:
        storage_id = client.storages.add_storage(json_file)['data']['id']
    for f in files_response:
        f = f['data']
        if f['name'] == corename + '_us.json':
            file_id = f['id']
            files_response = client.translations.upload_translation(project_id, language_id, storage_id, file_id)
            return files_response['data']
    return


def crowdin_download_translations(client, project_id, file_id):
    langs = client.projects.get_project(project_id)['data']['targetLanguageIds']
    build_response = []
    for lang in langs:
        build_response.append(client.translations.build_project_file_translation(
            project_id, file_id, lang, skipUntranslatedStrings=True)['data']['url'])
    import urllib.request as req
    import cgi
    for url in build_response:
        remotefile = req.urlopen(url)
        remotefile_info = remotefile.info()['Content-Disposition']
        val, params = cgi.parse_header(remotefile_info)
        filename = params["filename"]
        req.urlretrieve(url, filename.lower())
        print(filename + ' retrieved')
    return


def crowdin_client(token: str):
    try:
        from crowdin_api import CrowdinClient
    except ModuleNotFoundError:
        print('A neccessary module (crowdin-api-client) was not found!')
        while True:
            u_input = input('Would you like me to install it for you (pip install crowdin-api-client)? (y/n')
            if u_input.lower() == 'y' or u_input.lower() == 'yes':
                import subprocess
                try:
                    process = subprocess.run(('python', '--version'), capture_output=True)
                    if process.stdout.startswith(b'Python 3'):
                        _python_call = 'python'
                    else:
                        _python_call = 'python3'
                except FileNotFoundError:
                    _python_call = 'python3'
                    pass
                print('Trying to Install required module: crowdin-api-client\n')
                print(_python_call + ' -m pip install crowdin-api-client')
                print('If this fails, please try to install this module manually.')
                subprocess.run((_python_call, '-m', 'pip', 'install', 'crowdin-api-client'))
                from crowdin_api import CrowdinClient
                break
            elif u_input.lower() == 'n' or u_input.lower() == 'no':
                print('\nSync with Crowdin cannot be performed! Exiting.')
                sys.exit(1)
            else:
                print('Invalid input! Try again.')
        pass
        # print('Module crowdin_api not found! Please install it:\npip install crowdin-api-client')
        # sys.exit(1)

    class FirstCrowdinClient(CrowdinClient):
        TOKEN = token

    client = FirstCrowdinClient()
    return client


# def set_core_name(corename):
#     if corename == '':
#         while corename == '':
#             corename = input('Please enter the name of the core: ')
#             corename = remove_special_chars(corename)
#         corename = corename.replace(' ', '_')
#         with open(os.path.realpath(__file__), 'r', encoding='utf-8') as py_file:
#             the_code = py_file.read()
#         with open(os.path.realpath(__file__), 'w', encoding='utf-8') as py_file:
#             py_file.write(re.sub(r"core_name = ''", f"core_name = '{corename}'", the_code, 1))
#     return corename


def is_viable_non_dupe(text, comparison):
    return 2 < len(text) and text != 'NULL' and text not in comparison


def is_viable_value(text):
    return 2 < len(text) and text != 'NULL' and text.lower() not in _on_offs


def create_non_dupe(base_name: str, opt_num: int, comparison):
    h = base_name
    if h in comparison:
        n = 0
        h = h + '_O' + str(opt_num)
        h_end = len(h)
        while h in comparison:
            h = h[:h_end] + '_' + str(n)
            n += 1
    return h


def get_texts(text):
    # all structs: group(0) full struct, group(1) beginning, group(2) content
    structs = cor.p_struct.finditer(text)
    hash_n_string = {}
    just_string = {}
    for struct_num, struct in enumerate(structs):
        struct_declaration = struct.group(1)
        struct_type_name = get_struct_type_name(struct_declaration)
        if 3 > len(struct_type_name):
            entry = '_us'
        else:
            entry = struct_type_name[2]
        if entry not in just_string:
            hash_n_string[entry] = {}
            just_string[entry] = set()

        is_v2 = False
        if 'retro_core_option_v2_definition' == struct_type_name[0]:
            is_v2 = True

        struct_content = struct.group(2)
        # 0: full option; 1: key; 2: description; 3: additional info; 4: key/value pairs
        struct_options = cor.p_option.finditer(struct_content)
        for opt, option in enumerate(struct_options):
            # group 1: key
            if option.group(1):
                opt_name = option.group(1)
                # no special chars allowed in key
                opt_name = remove_special_chars(opt_name).upper().replace(' ', '_')
            else:
                print(f'ERROR: No option name (key) found in struct {struct_type_name[1]} option {opt}!')
                sys.exit(1)

            # group 2: description0
            if option.group(2):
                desc0 = option.group(2)
                if is_viable_non_dupe(desc0, just_string[entry]):
                    just_string[entry].add(desc0)
                    m_h = create_non_dupe(re.sub(r'__+', '_', f'{opt_name}_LABEL'), opt, hash_n_string[entry])
                    hash_n_string[entry][m_h] = desc0
            else:
                print(f'ERROR: No label found in struct {struct_type_name[1]} option {option.group(1)}!')
                sys.exit(1)

            # group 3: desc1, info0, info1, category
            if option.group(3):
                option_info = cor.p_info.finditer(option.group(3))
                if is_v2:
                    desc1 = next(option_info).group(1)
                    if is_viable_non_dupe(desc1, just_string[entry]):
                        just_string[entry].add(desc1)
                        m_h = create_non_dupe(re.sub(r'__+', '_', f'{opt_name}_LABEL_CAT'), opt, hash_n_string[entry])
                        hash_n_string[entry][m_h] = desc1
                    last = None
                    m_h = None
                    for j, info in enumerate(option_info):
                        last = info.group(1)
                        if is_viable_non_dupe(last, just_string[entry]):
                            just_string[entry].add(last)
                            m_h = create_non_dupe(re.sub(r'__+', '_', f'{opt_name}_INFO_{j}'), opt,
                                                  hash_n_string[entry])
                            hash_n_string[entry][m_h] = last
                    if last in just_string[entry]:  # category key should not be translated
                        hash_n_string[entry].pop(m_h)
                        just_string[entry].remove(last)
                else:
                    for j, info in enumerate(option_info):
                        gr1 = info.group(1)
                        if is_viable_non_dupe(gr1, just_string[entry]):
                            just_string[entry].add(gr1)
                            m_h = create_non_dupe(re.sub(r'__+', '_', f'{opt_name}_INFO_{j}'), opt,
                                                  hash_n_string[entry])
                            hash_n_string[entry][m_h] = gr1
            else:
                print(f'ERROR: Too few arguments in struct {struct_type_name[1]} option {option.group(1)}!')
                sys.exit(1)

            # group 4:
            if option.group(4):
                for j, kv_set in enumerate(cor.p_key_value.finditer(option.group(4))):
                    set_key, set_value = kv_set.group(1, 2)
                    if not is_viable_value(set_value):
                        if not is_viable_value(set_key):
                            continue
                        set_value = set_key
                    # re.fullmatch(r'(?:[+-][0-9]+)+', value[1:-1])
                    if set_value not in just_string[entry] and not re.sub(r'[+-]', '', set_value[1:-1]).isdigit():
                        clean_key = set_key.encode('ascii', errors='ignore').decode('unicode-escape')
                        clean_key = remove_special_chars(clean_key).upper().replace(' ', '_')
                        m_h = create_non_dupe(re.sub(r'__+', '_', f"OPTION_VAL_{clean_key}"), opt, hash_n_string[entry])
                        hash_n_string[entry][m_h] = set_value
                        just_string[entry].add(set_value)
    return hash_n_string


# --------------------          MAIN          -------------------- #

if __name__ == '__main__':
    # core_name = set_core_name(core_name)
    _crowdin_file_path = _joiner.join((_dir_path, _core_name))

    print('Getting texts from libretro_core_options.h')
    try:
        with open(_h_file_path, 'r+', encoding='utf-8') as _h_file:
            _main_text = _h_file.read()
    except EnvironmentError:
        print(f'ERROR: Could not find/open {_h_file_path}!')
        sys.exit(1)
    _hash_n_str = get_texts(_main_text)
    _files = create_msg_hash(_crowdin_file_path, _hash_n_str)

    import json

    _source_jsons = options2json(_files)

    print('Initializing sync with crowdin')

    _client = crowdin_client(_api_token)

    for _source_lang in _source_jsons:
        if _source_lang == '_us':
            print(f'Upload {os.path.basename(_source_jsons[_source_lang])}')
            _upload_response = crowdin_upload_source(_client, _project_id, _source_jsons[_source_lang], _core_name)
            break
        else:
            print('Naming error, or you are trying to upload a non-English source file:')
            print(os.path.basename(_source_jsons[_source_lang]) + '\n')
            continue

    try:
        _upload_response
    except NameError:
        print('Source upload unsuccessful!')
        sys.exit(1)

    while True:
        _response = input('Would you like to upload present translations? (y/n)')
        if _response.lower() == 'y' or _response.lower() == 'yes':
            _upload_translations = True
            break
        elif _response.lower() == 'n' or _response.lower() == 'no':
            _upload_translations = True
            break
        else:
            print('Invalid input. Try again.\n')

    if _upload_translations:
        try:
            with open(_intl_file_path, 'r+', encoding='utf-8') as _intl_file:
                _intl_text = _intl_file.read()

            print('Uploading present translations:')
            _hash_n_str_intl = get_texts(_intl_text)
            _intl_files = create_msg_hash(_crowdin_file_path, _hash_n_str_intl)
            _intl_jsons = options2json(_intl_files)

            for _intl_lang in _intl_jsons:
                print(f'Uploading {os.path.basename(_intl_jsons[_intl_lang])}...')
                if _intl_lang == '_us':
                    print('    aborted')
                    continue
                else:
                    _intl_upload_response = crowdin_upload_translation(_client, _intl_jsons[_intl_lang], _project_id,
                                                                       _langs_to_id[_intl_lang], _core_name)
        except EnvironmentError:
            print(f'ERROR: Could not find/open {_h_file_path}!')
            pass

    print('Downloading translations from crowdin:')
    crowdin_download_translations(_client, _project_id, _upload_response['data']['id'])

    print('Converting translations *.json to *.h:')
    for _file in os.listdir(_dir_path):
        if _file.startswith(_core_name) and _file.endswith('.json'):
            print(_file)
            json2h(_file, _core_name)

    try:
        while True:
            u_inp = input('Construct libretro_core_options_intl.h? (y/n)\n')
            if u_inp.lower() == 'y' or u_inp.lower() == 'yes':
                print('Constructing libretro_core_options_intl.h')
                create_intl_file(_main_text, _core_name, _files['_us'])
                break
            elif u_inp.lower() == 'n' or u_inp.lower() == 'no':
                break
            else:
                print('Invalid input! Try again.')
    except KeyboardInterrupt:
        sys.exit(1)
    print('\nAll done!')
