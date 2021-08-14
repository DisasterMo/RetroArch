#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
import time
import urllib.request
import zipfile

if len(sys.argv) < 2:
    print('Please provide core_name!')
    exit()
core_name = sys.argv[1]

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_file = 'crowdin.yaml'
api_key = '____'

print('Convert to json')
if os.name == 'nt':
    python_call = 'python'
else:
    python_call = 'python3'

subprocess.run([python_call, 'options2json.py', core_name + '_us.h'])

try:
    while True:
        u_input = input('\nWould you like to sync with crowdin? (y/n)\n')
        if u_input == 'y' or u_input == 'yes':
            # Get Crowdin API Key
            api_key = input('Please provide Crowdin API key: ')

            import re

            # Apply Crowdin API Key
            crowdin_config_file = open(yaml_file, 'r')
            crowdin_config = crowdin_config_file.read()
            crowdin_config_file.close()
            crowdin_config = re.sub(re.escape('_secret_'), api_key, crowdin_config, 1)
            crowdin_config = crowdin_config.replace('msg_hash', core_name)
            crowdin_config_file = open(yaml_file, 'w')
            crowdin_config_file.write(crowdin_config)
            crowdin_config_file.close()

            # Download Crowdin CLI
            jar_name = 'crowdin-cli.jar'

            if not os.path.isfile(jar_name):
                print('Download crowdin-cli.jar')
                crowdin_cli_file = 'crowdin-cli.zip'
                crowdin_cli_url = 'https://downloads.crowdin.com/cli/v2/' + crowdin_cli_file
                urllib.request.urlretrieve(crowdin_cli_url, crowdin_cli_file)
                with zipfile.ZipFile(crowdin_cli_file, 'r') as zip_ref:
                    jar_dir = zip_ref.namelist()[0]
                    for file in zip_ref.namelist():
                        if file.endswith(jar_name):
                            jar_file = file
                    zip_ref.extract(jar_file)
                    os.rename(jar_file, jar_name)
                    os.remove(crowdin_cli_file)
                    shutil.rmtree(jar_dir)

            print('Upload source *.json')
            subprocess.run(['java', '-jar', 'crowdin-cli.jar', 'upload', 'sources'])
            print('Wait for crowdin server to process data (10s)...')
            time.sleep(10)
            print('Download translation jsons')
            subprocess.run(['java', '-jar', 'crowdin-cli.jar', 'download', 'translations'])
            print('Fetch translation progress')
            subprocess.run([python_call, 'fetch_progress.py'])
            break
        elif u_input == 'n' or u_input == 'no':
            print('Moving on then.')
            break
        else:
            print('Invalid input! Try again.')

    print('Convert translations *.json to *.h')
    for file in os.listdir(dir_path):
        if file.startswith(core_name) and file.endswith('.json'):
            print(file)
            subprocess.run([python_call, 'json2h.py', file, core_name])

except RuntimeError:
    # Reset Crowdin API Key
    crowdin_config_file = open(yaml_file, 'r')
    crowdin_config = crowdin_config_file.read()
    crowdin_config_file.close()
    crowdin_config = re.sub(re.escape(f'"{api_key}"'), '"_secret_"', crowdin_config, 1)
    crowdin_config = crowdin_config.replace('/' + core_name, '/msg_hash')
    crowdin_config_file = open(yaml_file, 'w')
    crowdin_config_file.write(crowdin_config)
    crowdin_config_file.close()
