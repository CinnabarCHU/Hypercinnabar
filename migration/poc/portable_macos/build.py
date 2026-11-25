"""Build a portable Apple Silicon bundle on a macOS runner; no user installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from native_compat import rebuild as rebuild_native, audit as audit_native

HERE = Path(__file__).resolve().parent
NODE = '24.22.3'
PYTHON = '3.12.14'
PYTHON_RELEASE = '20260901'
ELECTRON = '44.11.6'
ASSETS = {
    'node': (f'https://nodejs.org/dist/v{NODE}/node-v{NODE}-darwin-arm64.tar.gz',
             'ff6e17d4874b76d272212b908cc020d6e815fba5a6c7eaaa06add725840307fd'),
    'python': (f'https://github.com/astral-sh/python-build-standalone/releases/download/{PYTHON_RELEASE}/cpython-{PYTHON}%2B{PYTHON_RELEASE}-aarch64-apple-darwin-install_only_stripped.tar.gz',
               '81a359f1cfadd4da11766534c5913791cea55f26e1bb902cacd2a531bb1e4b2b'),
}


def run(*args, **kw):
    print('+', ' '.join(str(x) for x in args), flush=True)
    subprocess.run([str(x) for x in args], check=True, **kw)


def download(name, destination):
    url, digest = ASSETS[name]
    file = destination / (name + '.tar.gz')
    if not file.exists():
        with urllib.request.urlopen(url, timeout=180) as response, file.open('wb') as output:
            shutil.copyfileobj(response, output)
    if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise ValueError(f'Unexpected {name} archive hash')
    return file


def build(kit, destination, staging):
    if os.uname().sysname != 'Darwin' or os.uname().machine != 'arm64':
        raise RuntimeError('Run this release build on macOS arm64.')
    if destination.exists():
        raise FileExistsError(destination)
    staging.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True)
    work = destination / 'Workspace'
    shutil.copytree(kit, work, ignore=shutil.ignore_patterns('.test-env', 'generated', '__pycache__'))
    shutil.copy2(HERE / 'portable_bootstrap.m', work / 'portable_bootstrap.m')
    shutil.copy2(HERE / 'README.zh-CN.md', destination / 'README.zh-CN.md')
    (destination / 'portable.json').write_text(json.dumps({'version':'0.7.1', 'arch':'arm64',
        'minimum_macos':'13.5', 'harness':'0.2.2-rc.5', 'acycle':'0.7.0',
        'electron':ELECTRON, 'python':PYTHON, 'node':NODE,
        'matlab':'external, R2024a target', 'bundled_api_key':False}, indent=2)+'\n')
    app_source = staging / 'app'
    shutil.copytree(HERE / 'app', app_source)
    run('npx','--yes','@electron/packager@20.3.0',app_source,'Acycle Harness',
        '--platform=darwin','--arch=arm64',f'--electron-version={ELECTRON}',
        f'--out={staging / "electron"}', '--overwrite', '--no-prune',
        '--app-bundle-id=org.hypercinnabar.acycle-harness-portable',
        '--app-version=0.7.1', '--darwin-dark-mode-support', '--app-category-type=public.app-category.education')
    built = staging / 'electron' / 'Acycle Harness-darwin-arm64' / 'Acycle Harness.app'
    app = destination / 'Acycle Harness.app'
    shutil.move(str(built), app)
    resources = app / 'Contents' / 'Resources'
    unpack = staging / 'unpacked'
    unpack.mkdir()
    for name in ('node','python'):
        archive = download(name, staging)
        with tarfile.open(archive) as tar:
            tar.extractall(unpack, filter='data')
    shutil.move(str(unpack / f'node-v{NODE}-darwin-arm64'), resources / 'node')
    shutil.move(str(unpack / 'python'), resources / 'python')
    python = resources / 'python' / 'bin' / 'python3'
    node = resources / 'node' / 'bin' / 'node'
    # The pure-Python wheel is installed at build time, offline, into this bundle.
    run(python,'-I','-m','pip','install','--no-index','--no-deps',
        work / 'packages' / 'acycle_deepseek-0.7.0-py3-none-any.whl')
    runtime = resources / 'runtime'
    runtime.mkdir()
    for name in ('package.json','package-lock.json'):
        shutil.copy2(HERE / 'runtime' / name, runtime / name)
    (runtime / 'packages').mkdir()
    shutil.copy2(work / 'packages' / 'dsh-acycle-0.7.0.tgz', runtime / 'packages')
    env = dict(os.environ)
    env['PATH'] = str(resources/'node'/'bin') + os.pathsep + env['PATH']
    run(node,resources/'node'/'lib'/'node_modules'/'npm'/'bin'/'npm-cli.js',
        'ci','--ignore-scripts','--no-audit','--no-fund',cwd=runtime,env=env)
    run(node,runtime/'node_modules'/'@deepseek-ai'/'dsh-subprocess-local'/'scripts'/'ensure-spawn-helper.mjs',env=env)
    rebuild_native(resources,staging,env)
    run(python,'-I','-c','import acycle_deepseek; import ssl; print("Bundled Python OK")')
    run(node,'--version')
    # Source and third-party LICENSE files remain in the distribution.
    import plistlib
    plist = app / 'Contents' / 'Info.plist'
    data = plistlib.loads(plist.read_bytes())
    data['LSMinimumSystemVersion'] = '13.5'
    plist.write_bytes(plistlib.dumps(data))
    audit_native(app)
    # Local ad-hoc signature; this is not Apple Developer ID notarization.
    run('codesign','--force','--deep','--sign','-',app)
    run('codesign','--verify','--deep','--strict',app)
    run('file',node,python,app/'Contents'/'MacOS'/'Acycle Harness')
    print(destination, flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit',required=True,type=Path)
    parser.add_argument('--destination',required=True,type=Path)
    parser.add_argument('--staging',required=True,type=Path)
    args=parser.parse_args()
    build(args.kit.resolve(),args.destination.resolve(),args.staging.resolve())
