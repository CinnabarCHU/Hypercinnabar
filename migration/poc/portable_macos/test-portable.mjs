import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {paths,prepare,environment,configure,readReadyUrl,matlabExpression,loadConnection} from './app/portable.mjs';

test('relocated bundle regenerates local absolute paths without overwriting user credentials',()=>{
  const base=mkdtempSync(join(tmpdir(),'acycle-portable-'));
  try{
    let root=join(base,'含 空格');mkdirSync(join(root,'Workspace','study'),{recursive:true});
    writeFileSync(join(root,'portable.json'),'{}');writeFileSync(join(root,'Workspace','start_local_demo.m'),'');
    let p=paths(root,join(root,'Acycle Harness.app','Contents','Resources'));prepare(p);
    writeFileSync(join(p.home,'.credentials.yaml'),'refs: {}\n');
    configure(p,{workspace:join(p.workspace,'study'),guiSession:join(p.tmp,'session'),matlabExecutable:'/Applications/MATLAB_R2024a.app/bin/matlab'});
    const moved=join(base,'Moved');renameSync(root,moved);
    p=paths(moved,join(moved,'Acycle Harness.app','Contents','Resources'));
    const plugin=configure(p,{workspace:join(p.workspace,'study'),guiSession:join(p.tmp,'new-session')});
    assert.equal(plugin.config.workspace,join(moved,'Workspace','study'));
    assert.ok(plugin.config.python.startsWith(moved));
    assert.equal(readFileSync(join(p.home,'.credentials.yaml'),'utf8'),'refs: {}\n');
    const env=environment(p,{HOME:'/real/home',PATH:'/untrusted',PYTHONHOME:'/system',NODE_OPTIONS:'--bad'});
    assert.equal(env.HOME,'/real/home');assert.equal(env.DSH_HOME,p.home);
    assert.equal(env.PYTHONHOME,undefined);assert.equal(env.NODE_OPTIONS,undefined);
    assert.ok(env.PATH.startsWith(join(p.resources,'node','bin')));
    assert.throws(()=>loadConnection(p));
  }finally{rmSync(base,{recursive:true,force:true});}
});
test('only an actual local Host ready line is accepted',()=>{
  assert.equal(readReadyUrl('other http://127.0.0.1:12/?token=x'),null);
  assert.equal(readReadyUrl('dsh web: http://example.com:12/?token=x'),null);
  assert.equal(readReadyUrl('dsh web: http://127.0.0.1:1234/?token=x\n'),'http://127.0.0.1:1234/?token=x');
  assert.equal(matlabExpression("/tmp/a'b/boot.m"),"run('/tmp/a''b/boot.m')");
});
