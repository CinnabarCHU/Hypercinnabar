"""Prepare and exercise the packaged plugin using the official Harness tool runtime."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT / '.test-env'
RUNTIME = ENVIRONMENT / 'harness'
VERSION = '0.2.2-rc.5'


def python_path():
    folder = ENVIRONMENT / 'python'
    return folder / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def node_path():
    node = shutil.which('node')
    if node is None:
        raise RuntimeError('Install Node.js 24.9 or later, then open a new terminal.')
    raw = subprocess.check_output([node, '--version'], text=True).strip()
    version = tuple(int(part) for part in raw.lstrip('v').split('.')[:2])
    if version < (24, 9):
        raise RuntimeError('Node.js 24.9 or later is required. Found ' + raw)
    return node


def prepare():
    node = node_path()
    npm = shutil.which('npm')
    if npm is None:
        raise RuntimeError('Install npm with Node.js, then open a new terminal.')
    npm_paths = [Path(npm).resolve(), Path(node).parent / 'node_modules/npm/bin/npm-cli.js',
                 Path(npm).parent / 'node_modules/npm/bin/npm-cli.js']
    npm_script = next((p for p in npm_paths if p.suffix == '.js' and p.is_file()), None)
    if npm_script:
        npm_command = [node, str(npm_script)]
    elif os.name != 'nt':
        npm_command = [npm]
    else:
        raise RuntimeError('The npm-cli.js supplied with Node.js could not be located.')
    wheel = ROOT / 'packages/acycle_deepseek-0.7.0-py3-none-any.whl'
    plugin = ROOT / 'packages/dsh-acycle-0.7.0.tgz'
    if not wheel.is_file() or not plugin.is_file():
        raise RuntimeError('Extract the complete ZIP before preparing the environment.')
    if not python_path().is_file():
        venv.EnvBuilder(with_pip=True).create(ENVIRONMENT / 'python')
    subprocess.run([str(python_path()), '-m', 'pip', 'install', '--no-index', '--no-deps', str(wheel)], check=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    package_file = RUNTIME / 'package.json'
    if not package_file.exists():
        package_file.write_text('{"name":"acycle-local-test-runtime","private":true}\n',encoding='utf-8')
    packages = ['dsh-tools','dsh-system-prompt','dsh-skill','dsh-tool-executor-native']
    subprocess.run(npm_command + ['install','--prefix',str(RUNTIME),'--save-exact','--no-fund','--no-audit'] +
                   ['@deepseek-ai/' + name + '@' + VERSION for name in packages] + [str(plugin)], check=True)
    print('Prepared the Python wheel and official Harness tool runtime.')
    print('Run start_local_demo in MATLAB, then run this script with check.')


def configuration():
    if not python_path().is_file():
        raise RuntimeError('Run local_test.py prepare first.')
    connection_file = ROOT / 'generated/connection.json'
    if not connection_file.is_file():
        raise RuntimeError('Run start_local_demo in MATLAB and keep its desktop open.')
    connection = json.loads(connection_file.read_text(encoding='utf-8'))
    if connection.get('protocol') != 1 or not (Path(connection['guiSession']) / 'session.json').is_file():
        raise RuntimeError('This MATLAB session has closed. Run start_local_demo again.')
    if Path(connection['workspace']).resolve() != (ROOT / 'study').resolve():
        raise RuntimeError('The demo directory moved. Run start_local_demo again in its current folder.')
    plugin = {'id':'acycle-native','name':'dsh-acycle','config':{
        'python':str(python_path()), 'workspace':connection['workspace'],
        'guiSession':connection['guiSession']}}
    output = ROOT / 'generated/harness-plugin.json'
    output.write_text(json.dumps(plugin,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','config','check','filter','image','events'])
    args = parser.parse_args()
    if sys.version_info < (3,10):
        parser.error('Python 3.10 or later is required.')
    try:
        if args.action == 'prepare':
            prepare()
            return 0
        config = configuration()
        if args.action == 'config':
            print(config)
            print(config.read_text(encoding='utf-8'))
            return 0
        node = node_path()
        if not (RUNTIME / 'node_modules/dsh-acycle/index.mjs').is_file():
            raise RuntimeError('Run local_test.py prepare to install the native tool runtime.')
        subprocess.run([node,str(ROOT/'check_harness.mjs'),str(config),args.action],check=True)
        return 0
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as error:
        print(str(error),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
