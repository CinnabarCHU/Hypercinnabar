"""Rebuild the pinned internal-loader addon for Ventura and audit Mach-O minima."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

SOURCE = 'https://github.com/deepseek-ai/dsh-node-addon-require-builtin.git'
COMMIT = 'a58d3599a2e551d7d706d1ff796c9fd4bbaff63c'
OMITTED = ['sherpa-onnx-darwin-arm64', '@deepseek-ai/dsh-experimental-cua-macos']


def run(*args, **kwargs):
    print('+', ' '.join(map(str,args)), flush=True)
    subprocess.run(list(map(str,args)),check=True,**kwargs)


def rebuild(resources, staging, env):
    source=staging/'native-addon-source'
    run('git','clone','--no-checkout',SOURCE,source)
    run('git','checkout','--detach',COMMIT,cwd=source)
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    assert actual==COMMIT
    assert json.loads((source/'package.json').read_text())['version']=='0.1.9'
    toolchain=staging/'native-addon-toolchain'
    toolchain.mkdir()
    (toolchain/'package.json').write_text('{"private":true}\n')
    node=resources/'node/bin/node'
    npm=resources/'node/lib/node_modules/npm/bin/npm-cli.js'
    run(node,npm,'install','--ignore-scripts','--no-audit','--no-fund','--save-exact',
        'tsx@4.20.6','node-addon-api@8.9.0',cwd=toolchain,env=env)
    (source/'node_modules').symlink_to(toolchain/'node_modules',target_is_directory=True)
    compiler=staging/'ventura-clang++'
    compiler.write_text('#!/bin/sh\nexec /usr/bin/clang++ -mmacosx-version-min=13.5 "$@"\n')
    compiler.chmod(0o755)
    build_env=dict(env,MACOSX_DEPLOYMENT_TARGET='13.5',CXX=str(compiler),NARB_PRODUCT='require-builtin',
        NARB_BACKEND='napi',NARB_BUILD_OUTPUT='prebuild',NODE_INCLUDE_DIR=str(resources/'node/include/node'))
    run(node,toolchain/'node_modules/tsx/dist/cli.mjs',source/'scripts/build.ts',cwd=source,env=build_env)
    binary=source/'packages/require-builtin/darwin-arm64/prebuilt/darwin-arm64-napi-v9.node'
    runtime=resources/'runtime'
    target=runtime/'node_modules/node-addon-require-builtin-darwin-arm64/prebuilt/darwin-arm64-napi-v9.node'
    assert json.loads((runtime/'node_modules/node-addon-require-builtin/package.json').read_text())['version']=='0.1.9'
    shutil.copy2(binary,target)
    # These unmounted speech and general computer-use binaries require macOS 14.
    # Acycle's preset uses its own MATLAB GUI protocol, not those experimental bundles.
    for package in OMITTED:
        optional=runtime/'node_modules'/package
        if optional.exists():shutil.rmtree(optional)
    test="const a=require('node-addon-require-builtin');const s=a.requireBuiltin('internal/modules/esm/loader');const c=a.requireBuiltin('internal/modules/cjs/loader');if(!s||!c)throw Error('Native bridge failed');console.log(JSON.stringify(a.getBindingInfo()));"
    run(node,'-e',test,cwd=runtime,env=dict(env,NARB_DISABLE_NATIVE_CACHE='1'))
    notices=resources/'native-build'
    notices.mkdir()
    shutil.copy2(source/'LICENSE',notices/'node-addon-require-builtin-LICENSE')
    (notices/'provenance.json').write_text(json.dumps({'source':SOURCE,'commit':COMMIT,'version':'0.1.9',
        'deployment_target':'13.5','binary_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'omitted_optional_packages':OMITTED},indent=2)+'\n')


def minimum_versions(path):
    with path.open('rb') as f:
        head=f.read(65536)
        if head[:4]==b'\xca\xfe\xba\xbe':
            for i in range(struct.unpack_from('>I',head,4)[0]):
                cpu,_,offset,_,_=struct.unpack_from('>IIIII',head,8+20*i)
                if cpu==0x100000c:
                    f.seek(offset);head=f.read(65536);break
        if head[:4]!=b'\xcf\xfa\xed\xfe' or struct.unpack_from('<I',head,4)[0]!=0x100000c:
            return []
        versions=[];offset=32
        for _ in range(struct.unpack_from('<I',head,16)[0]):
            command,size=struct.unpack_from('<II',head,offset)
            if command in (0x32,0x24):
                v=struct.unpack_from('<I',head,offset+(12 if command==0x32 else 8))[0]
                versions.append((v>>16,(v>>8)&255,v&255))
            offset+=size
        return versions


def audit(app):
    records=[]
    for path in app.rglob('*'):
        if not path.is_file() or path.is_symlink():continue
        # Every Mach-O file, including executables without extensions.
        with path.open('rb') as f:magic=f.read(4)
        if magic not in (b'\xcf\xfa\xed\xfe',b'\xca\xfe\xba\xbe'):continue
        versions=minimum_versions(path)
        if not versions:continue
        if any(v>(13,5,0) for v in versions):
            raise RuntimeError(f'{path} requires macOS {versions}, beyond Ventura 13.5')
        records.append({'path':str(path.relative_to(app)),'minimum_versions':versions})
    result={'status':'passed','target':'macOS 13.5 arm64','checked_binaries':len(records),'binaries':records}
    (app/'Contents/Resources/native-build/macos-minimums.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Ventura binary audit passed:',len(records),'Mach-O files',flush=True)
